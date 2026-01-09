from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.parameter_spec import (
    ParameterSpec,
)
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec


@dataclass
class AttributeMapper:

    def to_parameter_spec(
        self,
        attribute: AttributeSpec,
        default_field_flavor: FieldFlavor | None = None,
    ) -> ParameterSpec:
        return ParameterSpec.create(
            name=attribute.name,
            annotation=attribute.type,
            optional=attribute.optional,
            default_field_flavor=default_field_flavor,
        )

    def to_attribute(self, parameter_spec: ParameterSpec) -> AttributeSpec:
        return AttributeSpec(
            name=parameter_spec.name,
            type=parameter_spec.annotation.render(),
            optional=parameter_spec.optional,
        )

    def to_parameter_specs(
        self,
        attributes: list[AttributeSpec],
        default_field_flavor: FieldFlavor | None = None,
    ) -> list[ParameterSpec]:
        return [
            self.to_parameter_spec(attr, default_field_flavor) for attr in attributes
        ]

    def to_attributes(
        self, parameter_specs: list[ParameterSpec]
    ) -> list[AttributeSpec]:
        return [self.to_attribute(spec) for spec in parameter_specs]
