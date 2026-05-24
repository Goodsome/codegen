from pathlib import Path
from codegen.code_metadata.application.dtos.file_collection import FileCollection
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.mappers.parsed_component_to_sync_data import ParsedComponentToSyncData
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.code_metadata.application.services.memory_component_collection import MemoryComponentCollection
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.reference_source import ReferenceSource
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from dataclasses import dataclass


@dataclass
class ProjectSyncService:
    parser: CodeParser
    file_system_port: FileSystemPort
    component_policy_factory: ComponentPolicyFactory
    uow: UnitOfWork[ComponentRepository]
    path_parser: PathParser
    
    def get_component(
        self,
        context: str,
        component_name: str,
    ) -> Component | None:
        with self.uow:
            components = self.uow.repository.find_by_context_names({(context, component_name)})
            return components.get((context, component_name))
        

    def reverse_code(
        self,
        context: str,
        component_type: str | None,
        component_name: str | None,
    ):
        file_collections = self._collect_files(
            context=context,
            component_type=component_type,
            component_name=component_name,
        )
        existing_dependencies = self._get_existing_components(file_collections)
        self._sync_components(file_collections, existing_dependencies)

    def _collect_files(
        self,
        context: str,
        component_type: str | None,
        component_name: str | None,
    ) -> list[FileCollection]:
        
        result: list[FileCollection] = []
        path = Path(f"src/codegen/{context}")
        
        pattern = "*.py"
        if component_name is not None:
            pattern = f"{SnakeString(component_name)}.py"
        if component_type is not None:
            policy =  self.component_policy_factory.get_policy(ComponentType(component_type))
            pattern = f"{policy.dir_name}/{pattern}"
        for file_path in self.file_system_port.list_directory_recursively(
            path=path, pattern=pattern
        ):
            if "interfaces" in str(file_path):
                continue
            file_name = file_path.stem
            if file_name in ["__init__", "container", "expr_def", "parsed_expr", "_convert", "ast_stmt", "ast_expr", "match_pattern"]:
                continue
            code = self.file_system_port.read_file(file_path)
            parsed_path = self.path_parser.parse_file_path(file_path)
            parsed_component = self.parser.parse(
                code=code, 
                component_name=PascalString(file_name),
            )
            reference_sources = self._collect_reference_sources(file_path, parsed_component)
            result.append(
                FileCollection(
                    context=parsed_path.context,
                    code=code,
                    type=parsed_path.component_type,
                    layer=parsed_path.layer,
                    name=PascalString(file_name),
                    path=file_path,
                    parsed_component=parsed_component,
                    reference_sources=reference_sources,
                )
            )
        return result

    def _collect_reference_sources(self, file_path: Path, parsed_component: ParsedComponent) -> list[ReferenceSource]:
        reference_sources: list[ReferenceSource] = []
        for import_dto in parsed_component.imports:
            if import_dto.level == 0:
                module = import_dto.module or ""
            else:
                parts = file_path.parts[:-import_dto.level]
                module = ".".join(parts) + "." + (import_dto.module or "")
            
            parsed_path = self.path_parser.parse_module_path(
                module,
            )
            reference_sources.append(
                ReferenceSource(
                    context=parsed_path.context,
                    components=import_dto.names,
                )
            )

        return reference_sources

    def _get_existing_components(
        self,
        file_collections: list[FileCollection],
    ) -> dict[tuple[str, str], Component]:
        context_names: set[tuple[str, str]] = set()
        contexts_only: set[str] = set()
        for fc in file_collections:
            context_names.add((fc.context, fc.name))
            context_names.update(fc.collect_dependency_components())
            contexts_only.update(fc.collect_dependency_contexts_only())
            
        with self.uow:
            existing_components = self.uow.repository.find_by_context_names(
                context_names=context_names
            )
            existing_dependencies_by_context = self.uow.repository.find_by_contexts(
                contexts=contexts_only
            )
            existing_components.update(existing_dependencies_by_context)
                    
        return existing_components

    def _sync_components(
        self,
        file_collections: list[FileCollection],
        existing_components: dict[tuple[str, str], Component],
    ) -> None:
        
        id_maps = {
            c.id: c for c in existing_components.values()
        }
        component_collection = MemoryComponentCollection(
            store=existing_components,
            components=id_maps,
        )
        for f in file_collections:
            component = component_collection.get_or_create_component(f.context, f.name)
            resolver = ReferenceResolver(
                component=component,
                components=component_collection,
                reference_sources=f.reference_sources,
            )
            mapper = ParsedComponentToSyncData(resolver=resolver)
            component_sync_data = mapper.map(
                context=f.context,
                parsed_component=f.parsed_component,
                component_type=f.type,
                layer=f.layer,
            )
            component.update(component_sync_data=component_sync_data)
            component_collection.update(component=component)
            
        with self.uow:
            for component in component_collection.need_saves.values():
                self.uow.repository.save(component)
            self.uow.commit()
