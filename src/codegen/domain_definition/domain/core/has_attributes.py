from typing import Self, Iterable

from codegen.domain_definition.domain.core.named_element_ops_mixin import NamedElementOpsMixin
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec

from pydantic import BaseModel, Field


class HasAttributes(BaseModel, NamedElementOpsMixin):
    """能力：拥有内部状态（属性）"""
    
    attributes: list[AttributeSpec] = Field(default_factory=list)
    
    def add_attribute(self: Self, attribute: AttributeSpec) -> Self:
        return self._add_item('attributes', attribute, 'Attribute')

    def update_attribute(self: Self, attribute: AttributeSpec) -> Self:
        return self._update_item('attributes', attribute, 'Attribute')

    def remove_attribute(self: Self, name: SnakeString) -> Self:
        return self._remove_item('attributes', name)

    def get_attribute(self: Self, name: SnakeString) -> AttributeSpec:
        return self._get_item('attributes', name, 'Attribute')

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