from dataclasses import dataclass
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


@dataclass
class AttributeMapper:

    def to_parameter_spec(
        self, attribute: Attribute, in_pydantic_model: bool = False
    ) -> ParameterSpec:
        return ParameterSpec.create(
            name=attribute.name,
            annotation=attribute.type,
            optional=attribute.optional,
            in_pydantic_model=in_pydantic_model,
        )

    def to_attribute(self, parameter_spec: ParameterSpec) -> Attribute:
        return Attribute(
            name=parameter_spec.name,
            type=parameter_spec.annotation.render(),
            optional=parameter_spec.optional,
        )

    def to_parameter_specs(self, attributes: list[Attribute]) -> list[ParameterSpec]:
        return [self.to_parameter_spec(attr) for attr in attributes]

    def to_attributes(self, parameter_specs: list[ParameterSpec]) -> list[Attribute]:
        return [self.to_attribute(spec) for spec in parameter_specs]
