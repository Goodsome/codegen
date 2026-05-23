from pathlib import Path
from codegen.code_metadata.application.dtos.file_collection import FileCollection
from codegen.code_metadata.application.dtos.imported_component import ImportedComponent
from codegen.code_metadata.application.mappers.parsed_component_to_sync_data import ParsedComponentToSyncData
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.code_metadata.application.services.memory_component_collection import MemoryComponentCollection
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.enums.architecture_layer import ArchitectureLayer
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
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
        existing_dependencies = self._ensure_dependencies(file_collections)
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
            if file_name in ["__init__", "container"]:
                continue
            code = self.file_system_port.read_file(file_path)
            parsed_path = self.path_parser.parse_file_path(file_path)
            
            result.append(
                FileCollection(
                    context=parsed_path.context,
                    code=code,
                    type=parsed_path.component_type,
                    layer=parsed_path.layer,
                    name=PascalString(file_name),
                    path=file_path,
                )
            )
        return result

    def _ensure_dependencies(
        self,
        file_collections: list[FileCollection],
    ) -> dict[tuple[str, str], Component]:
        dependencies: set[ImportedComponent] = set()
        for fc in file_collections:
            import_components = self.parser.parse_dependencies(
                code=fc.code,
                component_path=fc.path
            )
            fc.import_components = import_components
            dependencies.update(import_components)
                
        context_names: set[tuple[str, str]] = {
            (ic.context, ic.name) for ic in dependencies
        }
        with self.uow:
            existing_dependencies = self.uow.repository.find_by_context_names(
                context_names=context_names
            )
            for dep in dependencies:
                if (dep.context, dep.name) not in existing_dependencies:
                    new_c = Component(
                        id=ComponentId.create(),
                        context=dep.context,
                        name=dep.name,
                        type=ComponentType.EXTERNAL,
                        layer=ArchitectureLayer.UNKNOWN,
                        description="",
                    )
                    self.uow.repository.add(new_c)
                    existing_dependencies[(dep.context, dep.name)] = new_c
                    
            self.uow.commit()

        for fc in file_collections:
            for ic in fc.import_components:
                component = existing_dependencies[(ic.context, ic.name)]
                fc.id_dependencies[component.id] = component

        return existing_dependencies

    def _sync_components(
        self,
        file_collections: list[FileCollection],
        existing_dependencies: dict[tuple[str, str], Component],
    ) -> None:
        
        context_names: set[tuple[str, str]] = {
            (f.context, f.name) for f in file_collections
        }
        id_maps = {
            c.id: c for c in existing_dependencies.values()
        }
        component_collection = MemoryComponentCollection(
            store=existing_dependencies,
            components=id_maps,
        )
        with self.uow:
            existing_components = self.uow.repository.find_by_context_names(
                context_names=context_names
            )
            for f in file_collections:
                if f.name in ["ExprDef", "ParsedExpr"]:
                    continue
                component = existing_components.get((f.context, f.name))
                if not component:
                    component = f.new_component()

                parsed_component = self.parser.parse(
                    code=f.code, 
                    component_name=f.name
                )
                reference_sources: list[ReferenceSource] = []
                for import_dto in parsed_component.imports:
                    parsed_path = self.path_parser.parse_module_path(
                        import_dto.module,
                    )
                    reference_sources.append(
                        ReferenceSource(
                            context=parsed_path.context,
                            components=import_dto.names,
                        )
                    )
                resolver = ReferenceResolver(
                    component=component,
                    id_map=f.id_dependencies,
                    components=component_collection,
                    reference_sources=reference_sources,
                )
                mapper = ParsedComponentToSyncData(resolver=resolver)
                component_sync_data = mapper.map(
                    context=f.context,
                    parsed_component=parsed_component,
                    component_type=f.type,
                    layer=f.layer,
                )
                component.update(component_sync_data=component_sync_data)
                self.uow.repository.save(component)

            for component in component_collection.need_saves.values():
                self.uow.repository.save(component)

            self.uow.commit()
