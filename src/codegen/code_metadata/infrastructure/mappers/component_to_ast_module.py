import ast
from collections import defaultdict
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.execptions.dep_component_not_found import (
    DependencyComponentNotFound,
)
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.infrastructure.mappers.component_to_ast_class import (
    ComponentToAstClass,
)


@dataclass
class ComponentToAstModule:
    component_to_ast_class: ComponentToAstClass
    component_policy_factory: ComponentPolicyFactory

    def map(
        self, component: Component, dep_components: dict[ComponentId, ComponentDTO]
    ) -> ast.Module:
        import_froms = self._get_import_froms(component, dep_components)
        class_def = self.component_to_ast_class.map(
            component, dep_components=dep_components
        )
        body: list[ast.stmt] = [
            *import_froms,
            class_def,
        ]
        module = ast.Module(
            body=body,
        )
        return module

    def _get_import_froms(
        self, component: Component, dep_components: dict[ComponentId, ComponentDTO]
    ) -> list[ast.ImportFrom]:
        collect_module_names: dict[str, set[str]] = defaultdict(set)
        for dep_id in component.get_dependencies():
            if dep_id not in dep_components:
                raise DependencyComponentNotFound(component_id=dep_id)
            dep_component = dep_components[dep_id]
            policy = self.component_policy_factory.get_policy(
                component_type=ComponentType(dep_component.type)
            )
            module = policy.get_import_module(
                context=dep_component.context,
                component_name=dep_component.name,
            )
            collect_module_names[module].add(dep_component.name)

        result: list[ast.ImportFrom] = []
        for module, names in sorted(collect_module_names.items()):
            import_from = ast.ImportFrom(
                module=module,
                names=[ast.alias(name=name) for name in names],
                level=0,
            )
            result.append(import_from)
        return result
