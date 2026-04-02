from typing import Self, Iterable

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec

from pydantic import BaseModel, Field


class HasAttributes(BaseModel):
    """能力：拥有内部状态（属性）"""
    
    attributes: list[AttributeSpec] = Field(default_factory=list)
    
    def add_attribute(self: Self, attribute: AttributeSpec) -> Self:
        """Add an AttributeSpec. Raises ValueError if attribute with same name exists."""
        for attr in self.attributes:
            if attr.name == attribute.name:
                raise ValueError(
                    f"Attribute '{attribute.name}' already exists in '{self}'"
                )
        self.attributes.append(attribute)
        return self

    def update_attribute(self: Self, attribute: AttributeSpec) -> Self:
        """Update an existing AttributeSpec by name. Raises ValueError if not found."""
        for i, attr in enumerate(self.attributes):
            if attr.name == attribute.name:
                self.attributes[i] = attribute
                return self
        raise ValueError(
            f"Attribute '{attribute.name}' not found in '{self}'"
        )

    def remove_attribute(self: Self, name: SnakeString) -> Self:
        """Remove an AttributeSpec by name. Returns self for chaining."""
        self.attributes = [attr for attr in self.attributes if attr.name != name]
        return self

    def get_attribute(self: Self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec by name. Raises ValueError if not found."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        raise ValueError(f"Attribute '{name}' not found in '{self}'")

    def to_variable_specs(self, flavor: FieldFlavor | None = None) -> list[VariableSpec]:
        """将 HasAttributes 转换为 PythonGen VariableSpec 列表"""
        return [
            attr.to_variable_spec(flavor=flavor)
            for attr in self.attributes
        ]
    
    @classmethod
    def from_variable_specs(cls: type[Self], specs: Iterable[VariableSpec]) -> list[AttributeSpec]:
        """将 VariableSpec 列表逆向解析为 HasAttributes"""
        return [
            AttributeSpec.from_variable_spec(spec)
            for spec in specs
        ]