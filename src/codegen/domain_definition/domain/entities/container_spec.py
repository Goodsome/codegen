from typing import TYPE_CHECKING

from pydantic import Field

from codegen.domain_definition.domain.value_objects.port_binding import PortBinding
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity

if TYPE_CHECKING:
    from codegen.domain_definition.domain.entities.bounded_context import BoundedContext
    from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec


class ContainerSpec(Entity):
    """Specification for a container (dependency injection)."""

    bindings: list[PortBinding] = Field(default_factory=list)

    def to_class_spec(
        self,
        context: "BoundedContext",
        class_name: str = "Container",
    ) -> ClassSpec:
        """将 ContainerSpec 转换为 ClassSpec"""
        attributes: list[VariableSpec] = []

        for binding in self.bindings:
            provider_var = self._create_provider_variable(binding)
            if provider_var:
                attributes.append(provider_var)

        for use_case in context.application.use_cases:
            provider_var = self._create_use_case_provider_variable(use_case)
            if provider_var:
                attributes.append(provider_var)

        return ClassSpec.create(
            name=class_name,
            inheritance=["DeclarativeContainer"],
            attributes=attributes,
        )

    def to_module_spec(
        self,
        context: "BoundedContext",
        class_name: str = "Container",
    ) -> ModuleSpec:
        """将 ContainerSpec 转换为 ModuleSpec"""
        class_spec = self.to_class_spec(context, class_name)
        return ModuleSpec.create(
            name="container",
            classes=[class_spec],
        )

    def to_app_container_module(self) -> ModuleSpec:
        """创建 app-level Container 模块"""
        from codegen.domain_definition.domain.entities.bounded_context import BoundedContext

        dummy_context = BoundedContext.create(name="App")
        container_class = self.to_class_spec(
            context=dummy_context,
            class_name="Container",
        )

        imports = [
            ImportFromSpec.create(
                module="dependency_injector.containers",
                names=["DeclarativeContainer"],
            ),
            ImportFromSpec.create(
                module="dependency_injector.providers",
                names=["Factory", "Singleton", "Configuration"],
            ),
        ]

        for binding in self.bindings:
            impl_module = SnakeString(binding.implementation.split('.')[0])
            impl_name = binding.implementation.split(".")[-1]
            imports.append(
                ImportFromSpec.create(
                    module=f"..{impl_module}.infrastructure.adapters",
                    names=[impl_name],
                )
            )

        return ModuleSpec.create(
            name="container",
            classes=[container_class],
            imports=imports,
        )

    def _create_provider_variable(self, binding: PortBinding) -> VariableSpec | None:
        """创建 provider VariableSpec"""
        implementation_name = binding.implementation
        provider_name = SnakeString(implementation_name)
        assignment = AssignmentSpec.from_call(
            func_name="Factory",
            args=[AssignmentSpec.from_symbol(implementation_name)],
        )
        return VariableSpec.create(
            name=str(provider_name),
            type_spec=None,
            assignment=assignment,
        )

    def _create_use_case_provider_variable(
        self, use_case: "UseCaseSpec"
    ) -> VariableSpec | None:
        """创建 use_case provider VariableSpec"""
        use_case_name = use_case.name
        provider_name = SnakeString(use_case_name)

        kwargs: dict[str, AssignmentSpec] = {}
        for dep in use_case.dependencies:
            for binding in self.bindings:
                if binding.port == dep.type:
                    kwarg_impl_name = SnakeString(binding.implementation)
                    kwargs[dep.name] = AssignmentSpec.from_symbol(str(kwarg_impl_name))
                    break

        assignment = AssignmentSpec.from_call(
            func_name="Factory",
            args=[AssignmentSpec.from_symbol(use_case_name)],
            kwargs=kwargs,
        )
        return VariableSpec.create(
            name=str(provider_name),
            type_spec=None,
            assignment=assignment,
        )
