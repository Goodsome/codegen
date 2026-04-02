from typing import Iterable, Self

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.core.named_element_ops_mixin import NamedElementOpsMixin
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec


class HasOperations(BaseModel, NamedElementOpsMixin):
    """能力：拥有操作（方法）"""

    operations: list[MethodSpec] = Field(default_factory=list)

    def add_operation(self: Self, operation: MethodSpec) -> Self:
        return self._add_item("operations", operation, "Operation")

    def update_operation(self: Self, operation: MethodSpec) -> Self:
        return self._update_item("operations", operation, "Operation")

    def remove_operation(self: Self, name) -> Self:
        return self._remove_item("operations", name)

    def get_operation(self: Self, name) -> MethodSpec:
        return self._get_item("operations", name, "Operation")

    def to_function_specs(self) -> list[FunctionSpec]:
        """将 HasOperations 转换为 PythonGen FunctionSpec 列表"""
        return [op.to_function_spec() for op in self.operations]

    @classmethod
    def from_function_specs(cls: type[Self], specs: Iterable[FunctionSpec]) -> list[MethodSpec]:
        """将 FunctionSpec 列表逆向解析为 HasOperations"""
        return [MethodSpec.from_function_spec(spec) for spec in specs]
