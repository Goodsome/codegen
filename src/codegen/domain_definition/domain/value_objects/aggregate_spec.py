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

    def add_behavior(self, behavior: MethodSpec) -> "AggregateSpec":
        if any(b.name == behavior.name for b in self.behaviors):
            raise ValueError(f"Behavior '{behavior.name}' already exists in aggregate '{self.name}'.")
        return self.model_copy(update={"behaviors": self.behaviors + [behavior]})

    def update_behavior(self, behavior: MethodSpec) -> "AggregateSpec":
        if not any(b.name == behavior.name for b in self.behaviors):
            raise ValueError(f"Behavior '{behavior.name}' not found in aggregate '{self.name}'.")
        new_behaviors = [behavior if b.name == behavior.name else b for b in self.behaviors]
        return self.model_copy(update={"behaviors": new_behaviors})

    def delete_behavior(self, name: str) -> "AggregateSpec":
        new_behaviors = [b for b in self.behaviors if str(b.name) != name]
        if len(new_behaviors) == len(self.behaviors):
            raise ValueError(f"Behavior '{name}' not found in aggregate '{self.name}'.")
        return self.model_copy(update={"behaviors": new_behaviors})

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
