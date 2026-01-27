from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec


class AggregateSpec(ValueObject):
    """Specification of a domain aggregate to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    behaviors: list[MethodSpec] = Field(default_factory=list)

    def add_attribute(self, attribute: AttributeSpec) -> "AggregateSpec":
        if any(a.name == attribute.name for a in self.attributes):
            raise ValueError(
                f"Attribute '{attribute.name}' already exists in aggregate '{self.name}'."
            )
        new_attributes = self.attributes + [attribute]
        return self.model_copy(update={"attributes": new_attributes})

    def update_attribute(self, attribute: AttributeSpec) -> "AggregateSpec":
        if not any(a.name == attribute.name for a in self.attributes):
            raise ValueError(
                f"Attribute '{attribute.name}' not found in aggregate '{self.name}'."
            )
        new_attributes = [
            attribute if a.name == attribute.name else a for a in self.attributes
        ]
        return self.model_copy(update={"attributes": new_attributes})

    def delete_attribute(self, name: str) -> "AggregateSpec":
        new_attributes = [a for a in self.attributes if str(a.name) != name]
        if len(new_attributes) == len(self.attributes):
            raise ValueError(
                f"Attribute '{name}' not found in aggregate '{self.name}'."
            )
        return self.model_copy(update={"attributes": new_attributes})
