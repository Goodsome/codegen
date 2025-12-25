"""
Kind: ValueObject
Name: ModuleSpec
Description: Represents a Python module.
"""

import re

from pydantic.fields import Field

from codegen.domain.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec


class ModuleSpec(ValueObject):
    """Represents a Python module."""

    filename: str
    functions: list[FunctionSpec] = Field(default_factory=list)
    classes: list[ClassSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        filename: str,
        functions: list[FunctionSpec] | None = None,
        classes: list[ClassSpec] | None = None,
    ) -> "ModuleSpec":
        filename = cls._to_snake_case(filename)
        if not filename.endswith(".py"):
            filename += ".py"
        return cls(
            filename=filename,
            functions=functions or [],
            classes=classes or [],
        )

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """内部工具：将字符串转换为 snake_case"""
        # 处理 CamelCase 或已有空格/横杠的情况
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower().replace("-", "_")

    def get_required_types(self) -> set[str]:
        """收集本模块所有需要的类型名称"""
        types: set[str] = set()
        for cls in self.classes:
            types.update(cls.get_required_types())
        for f in self.functions:
            types.update(f.get_required_types())
        return types

    def has_class(self, class_name: str) -> bool:
        """检查模块中是否存在指定名称的类"""
        return any(cls.name == class_name for cls in self.classes)

    def has_function(self, function_name: str) -> bool:
        """检查模块中是否存在指定名称的函数"""
        return any(f.name == function_name for f in self.functions)

    def has_class_or_function(self, name: str) -> bool:
        return self.has_class(name) or self.has_function(name)
