from typing import Iterable, Self

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.core.named_element_ops_mixin import NamedElementOpsMixin
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec


class HasDependencies(BaseModel, NamedElementOpsMixin):
    """能力：拥有依赖项"""

    dependencies: list[AttributeSpec] = Field(default_factory=list)

    def add_dependency(self: Self, dependency: AttributeSpec) -> Self:
        return self._add_item("dependencies", dependency, "Dependency")

    def update_dependency(self: Self, dependency: AttributeSpec) -> Self:
        return self._update_item("dependencies", dependency, "Dependency")

    def remove_dependency(self: Self, name) -> Self:
        return self._remove_item("dependencies", name)

    def get_dependency(self: Self, name) -> AttributeSpec:
        return self._get_item("dependencies", name, "Dependency")

    def to_variable_specs(self, flavor: FieldFlavor | None = None) -> list[VariableSpec]:
        """将 HasDependencies 转换为 PythonGen VariableSpec 列表"""
        return [dep.to_variable_spec(flavor=flavor) for dep in self.dependencies]

    @classmethod
    def from_variable_specs(cls: type[Self], specs: Iterable[VariableSpec]) -> list[AttributeSpec]:
        """将 VariableSpec 列表逆向解析为 HasDependencies"""
        return [AttributeSpec.from_variable_spec(spec) for spec in specs]
