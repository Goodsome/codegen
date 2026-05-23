import ast
from collections import defaultdict
from dataclasses import dataclass

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.infrastructure.mappers.component_to_ast_class import (
    ComponentToAstClass,
)


@dataclass
class ComponentToAstModule:
    resolver: ReferenceResolver
    component_to_ast_class: ComponentToAstClass
    component_policy_factory: ComponentPolicyFactory

    @classmethod
    def create(
        cls,
        component_policy_factory: ComponentPolicyFactory,
        resolver: ReferenceResolver,
    ) -> "ComponentToAstModule":
        component_to_ast_class = ComponentToAstClass.create(
            component_policy_factory=component_policy_factory,
            resolver=resolver,
        )
        return cls(
            resolver=resolver,
            component_to_ast_class=component_to_ast_class,
            component_policy_factory=component_policy_factory,
        )

    def map(
        self, component: Component
    ) -> ast.Module:
        import_froms = self._get_import_froms(component)
        class_def = self.component_to_ast_class.map(
            component
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
        self, component: Component
    ) -> list[ast.ImportFrom]:
        collect_module_names: dict[str, set[str]] = defaultdict(set)
        for dep_id in component.get_dependencies():
            dc = self.resolver.get_component(dep_id)
            policy = self.component_policy_factory.get_policy(
                component_type=dc.type
            )
            module = dc.get_import_module(policy)
            collect_module_names[module].add(dc.name)

        result: list[ast.ImportFrom] = []
        for module, names in sorted(collect_module_names.items()):
            import_from = ast.ImportFrom(
                module=module,
                names=[ast.alias(name=name) for name in names],
                level=0,
            )
            result.append(import_from)
        return result
