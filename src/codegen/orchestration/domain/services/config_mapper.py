from dataclasses import dataclass

from codegen.domain_definition.domain.value_objects.config_field_spec import (
    ConfigFieldSpec,
)
from codegen.domain_definition.domain.value_objects.config_spec import ConfigSpec
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec


@dataclass
class ConfigMapper:
    """Maps ConfigSpec to PythonGen ClassSpec for generating Pydantic BaseSettings classes."""

    def to_class_spec(
        self, config_spec: ConfigSpec, class_name: str | None = None
    ) -> ClassSpec:
        """
        Maps a ConfigSpec to a ClassSpec.

        Args:
            config_spec: The configuration specification
            class_name: Optional class name override (defaults to config_spec.class_name)

        Returns:
            ClassSpec representing a Pydantic BaseSettings class
        """
        name = (
            str(config_spec.class_name)
            if config_spec.class_name
            else (class_name or "Settings")
        )

        attributes: list[VariableSpec] = []

        for field in config_spec.fields:
            field_var = self._map_field_to_variable(field)
            attributes.append(field_var)

        if config_spec.env_prefix:
            model_config = self._create_model_config_attribute(config_spec)
            attributes.insert(0, model_config)

        return ClassSpec.create(
            name=name,
            inheritance=["BaseSettings"],
            attributes=attributes,
        )

    def _map_field_to_variable(self, field_spec: ConfigFieldSpec) -> VariableSpec:
        """Maps a ConfigFieldSpec to a VariableSpec."""
        type_spec = TypeAnnotationSpec.from_raw(field_spec.type)

        if field_spec.default is not None:
            assignment = AssignmentSpec.from_literal(field_spec.default)
        else:
            assignment = None

        return VariableSpec.create(
            name=str(field_spec.name),
            type_spec=type_spec,
            assignment=assignment,
        )

    def _create_model_config_attribute(self, config_spec: ConfigSpec) -> VariableSpec:
        """Creates the model_config attribute for Pydantic BaseSettings."""
        kwargs = {}

        if config_spec.env_prefix:
            kwargs["env_prefix"] = AssignmentSpec.from_literal(config_spec.env_prefix)

        assignment = AssignmentSpec.from_call(
            func_name="SettingsConfigDict",
            kwargs=kwargs,
        )

        return VariableSpec.create(
            name="model_config",
            type_spec=None,
            assignment=assignment,
        )

    def to_module_spec(
        self, config_spec: ConfigSpec, class_name: str | None = None
    ) -> ModuleSpec:
        """
        Creates a ModuleSpec containing the Config class with required imports.

        Args:
            config_spec: The configuration specification
            class_name: Optional class name override

        Returns:
            ModuleSpec for config.py
        """
        class_spec = self.to_class_spec(config_spec, class_name)

        imports = [
            ImportFromSpec.create(
                module="pydantic_settings",
                names=["BaseSettings", "SettingsConfigDict"],
            )
        ]

        return ModuleSpec.create(
            name="config",
            classes=[class_spec],
            imports=imports,
        )
