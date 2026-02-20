from dataclasses import dataclass

from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.container_spec import ContainerSpec
from codegen.domain_definition.domain.value_objects.port_binding import PortBinding
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec


@dataclass
class ContainerMapper:
    """Maps ContainerSpec to PythonGen ClassSpec for generating dependency_injector containers."""

    def to_class_spec(
        self,
        container_spec: ContainerSpec,
        context: BoundedContext,
        class_name: str = "Container",
    ) -> ClassSpec:
        """
        Maps a ContainerSpec to a ClassSpec.

        Args:
            container_spec: The container specification with port bindings
            context: The bounded context to resolve port implementations
            class_name: The name of the container class

        Returns:
            ClassSpec representing a DeclarativeContainer
        """
        attributes: list[VariableSpec] = []

        for binding in container_spec.bindings:
            provider_var = self._create_provider_variable(binding, context)
            if provider_var:
                attributes.append(provider_var)

        return ClassSpec.create(
            name=class_name,
            inheritance=["DeclarativeContainer"],
            attributes=attributes,
        )

    def _create_provider_variable(
        self, binding: PortBinding, context: BoundedContext
    ) -> VariableSpec | None:
        """
        Creates a provider VariableSpec from a PortBinding.

        Generates code like:
            port_name_impl = providers.Factory(PortImplClass)
        """
        implementation_name = binding.implementation
        provider_name = self._to_snake_case(implementation_name)

        assignment = self._create_provider_assignment(implementation_name)

        return VariableSpec.create(
            name=provider_name,
            type_spec=None,
            assignment=assignment,
        )

    def _create_provider_assignment(self, implementation_class: str) -> AssignmentSpec:
        """Creates a Factory(...) assignment."""
        return AssignmentSpec.from_call(
            func_name="Factory",
            args=[AssignmentSpec.from_code(implementation_class)],
        )

    def _to_snake_case(self, name: str) -> str:
        """Converts PascalCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def to_module_spec(
        self,
        container_spec: ContainerSpec,
        context: BoundedContext,
        class_name: str = "Container",
        project_name: str = "",
    ) -> ModuleSpec:
        """
        Creates a ModuleSpec containing the Container class with required imports.

        Args:
            container_spec: The container specification
            context: The bounded context to resolve implementations
            class_name: The name of the container class
            project_name: The root name of the project to create absolute imports

        Returns:
            ModuleSpec for container.py
        """
        class_spec = self.to_class_spec(container_spec, context, class_name)

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

        import_module = "..infrastructure.adapters"
        if project_name:
            import_module = f"{project_name}.{context.name.lower()}.infrastructure.adapters"

        for binding in container_spec.bindings:
            imports.append(
                ImportFromSpec.create(
                    module=import_module,
                    names=[binding.implementation],
                )
            )

        return ModuleSpec.create(
            name="container",
            classes=[class_spec],
            imports=imports,
        )
