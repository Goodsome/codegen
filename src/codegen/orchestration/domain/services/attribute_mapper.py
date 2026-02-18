from dataclasses import dataclass, field
from codegen.python_gen.domain.value_objects.parameter_spec import (
    ParameterSpec,
)
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.orchestration.domain.services.type_system_converter import (
    TypeSystemConverter,
)


@dataclass
class AttributeMapper:
    type_system_converter: TypeSystemConverter = field(default_factory=TypeSystemConverter)

    def to_parameter_spec(
        self,
        attribute: AttributeSpec,
        default_field_flavor: FieldFlavor | None = None,
    ) -> ParameterSpec:
        annotation = self.type_system_converter.to_python_annotation(attribute)

        return ParameterSpec.create(
            name=attribute.name,
            annotation=annotation,
            optional=attribute.optional,
            default_field_flavor=default_field_flavor,
        )

    def to_attribute(self, parameter_spec: ParameterSpec) -> AttributeSpec:
        generic_type, container, is_optional, custom_type_string = (
            self.type_system_converter.from_python_annotation(parameter_spec.annotation)
        )

        return AttributeSpec(
            name=parameter_spec.name,
            type=generic_type,
            container=container,
            optional=is_optional,
            custom_type_string=custom_type_string,
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
