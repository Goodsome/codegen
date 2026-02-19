from dataclasses import dataclass, field

from codegen.domain_definition.domain.value_objects.blueprint import Blueprint
from codegen.domain_definition.domain.value_objects.bootstrap_spec import BootstrapSpec
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.config_spec import ConfigSpec
from codegen.domain_definition.domain.value_objects.container_spec import ContainerSpec
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.orchestration.domain.services.config_mapper import ConfigMapper
from codegen.orchestration.domain.services.container_mapper import ContainerMapper


@dataclass
class BootstrapMapper:
    """Maps BootstrapSpec to PythonGen PackageSpec for generating bootstrap code."""

    config_mapper: ConfigMapper = field(default_factory=ConfigMapper)
    container_mapper: ContainerMapper = field(default_factory=ContainerMapper)

    def to_package_spec(self, blueprint: Blueprint) -> PackageSpec | None:
        """
        Maps BootstrapSpec to a PackageSpec.

        This generates:
        - config.py: AppSettings with nested ContextSettings
        - container.py: Container with aggregated providers

        Args:
            blueprint: The blueprint containing bootstrap spec and contexts

        Returns:
            PackageSpec for bootstrap package, or None if no bootstrap spec
        """
        if not blueprint.bootstrap:
            return None

        bootstrap_spec = blueprint.bootstrap
        modules: list[ModuleSpec] = []

        # Generate config module if bootstrap has config
        if bootstrap_spec.config:
            config_module = self._create_app_config_module(
                bootstrap_spec.config, blueprint.contexts
            )
            modules.append(config_module)

        # Generate container module if bootstrap has container
        if bootstrap_spec.container:
            container_module = self._create_app_container_module(
                bootstrap_spec.container, blueprint.contexts
            )
            modules.append(container_module)

        if not modules:
            return None

        return PackageSpec.create(
            name="bootstrap",
            modules=modules,
        )

    def _create_app_config_module(
        self, bootstrap_config: ConfigSpec, contexts: list[BoundedContext]
    ) -> ModuleSpec:
        """
        Creates the AppSettings module aggregating all context configs.

        Args:
            bootstrap_config: The bootstrap-level config spec
            contexts: All bounded contexts with their configs

        Returns:
            ModuleSpec for config.py with AppSettings
        """
        # Create the AppSettings class
        app_settings = self.config_mapper.to_class_spec(
            bootstrap_config, class_name="AppSettings"
        )

        # Add nested context settings fields
        context_config_fields: list[VariableSpec] = []
        context_imports: list[ImportFromSpec] = []

        for context in contexts:
            if context.config:
                context_class_name = f"{context.name}Settings"

                # Create field: context_name = Field(default_factory=ContextSettings)
                field_assignment = AssignmentSpec.from_call(
                    func_name="Field",
                    kwargs={
                        "default_factory": AssignmentSpec.from_code(context_class_name)
                    },
                )

                field_var = VariableSpec.create(
                    name=self._to_snake_case(str(context.name)),
                    type_spec=None,  # Will be inferred from assignment
                    assignment=field_assignment,
                )
                context_config_fields.append(field_var)

                # Add import for context settings
                context_imports.append(
                    ImportFromSpec.create(
                        module=f"..{self._to_snake_case(str(context.name))}.config",
                        names=[context_class_name],
                    )
                )

        # Add context fields to AppSettings
        app_settings.attributes.extend(context_config_fields)

        # Build imports
        imports = [
            ImportFromSpec.create(
                module="pydantic_settings",
                names=["BaseSettings", "SettingsConfigDict"],
            ),
            ImportFromSpec.create(
                module="pydantic",
                names=["Field"],
            ),
        ]
        imports.extend(context_imports)

        return ModuleSpec.create(
            name="config",
            classes=[app_settings],
            imports=imports,
        )

    def _create_app_container_module(
        self, bootstrap_container: ContainerSpec, contexts: list[BoundedContext]
    ) -> ModuleSpec:
        """
        Creates the app-level Container module.

        Args:
            bootstrap_container: The bootstrap-level container spec
            contexts: All bounded contexts with their containers

        Returns:
            ModuleSpec for container.py
        """
        # For now, create a simple container with bootstrap bindings
        # TODO: Aggregate context-level providers

        # Create a dummy context with the bootstrap bindings for the mapper
        dummy_context = BoundedContext.create(name="App")

        container_class = self.container_mapper.to_class_spec(
            bootstrap_container,
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

        for binding in bootstrap_container.bindings:
            imports.append(
                ImportFromSpec.create(
                    module=f"..{self._to_snake_case(binding.implementation.split('.')[0])}.infrastructure.adapters",
                    names=[binding.implementation.split(".")[-1]],
                )
            )

        return ModuleSpec.create(
            name="container",
            classes=[container_class],
            imports=imports,
        )

    def _to_snake_case(self, name: str) -> str:
        """Converts PascalCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
