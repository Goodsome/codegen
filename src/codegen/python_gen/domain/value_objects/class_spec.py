"""
Kind: ValueObject
Name: ClassSpec
Description: Represents a class in a Python module.
"""

from pydantic.fields import Field

from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.core import ValueObject


class ClassSpec(ValueObject):
    """Represents a class in a Python module."""

    name: PascalString
    description: str = Field(default="")
    decorators: list[str] = Field(default_factory=list)
    inheritance: list[str] = Field(default_factory=list)
    attributes: list[VariableSpec] = Field(default_factory=list)
    methods: list[FunctionSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        decorators: list[str] | None = None,
        inheritance: list[str] | None = None,
        attributes: list[VariableSpec] | None = None,
        methods: list[FunctionSpec] | None = None,
    ) -> "ClassSpec":
        return cls(
            name=PascalString(name),
            description=description,
            decorators=decorators or [],
            inheritance=inheritance or [],
            attributes=attributes or [],
            methods=methods or [],
        )

    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        types.update(self.inheritance)
        types.update(self.decorators)
        for attribute in self.attributes:
            types.update(attribute.get_required_types())
        for method in self.methods:
            types.update(method.get_required_types())
        return types

    def get_method(self, method_name: str) -> FunctionSpec:
        """获取指定名称的方法，不存在则 raise error"""
        m = self.find_method(method_name=method_name)
        if m is None:
            raise ValueError(f"Method '{method_name}' not found in class '{self.name}'")
        else:
            return m

    def find_method(self, method_name: str) -> FunctionSpec | None:
        for method in self.methods:
            if method.name == method_name:
                return method
        return None

    def merge(self, other: "ClassSpec") -> "ClassSpec":
        if self.name != other.name:
            return self
        other_methods = {m.name: m for m in other.methods}
        methods: list[FunctionSpec] = []
        for m in self.methods:
            if m.name in other_methods:
                methods.append(m.merge(other_methods[m.name]))
            else:
                methods.append(m)
        return self.__class__.create(
            name=self.name,
            description=self.description,
            inheritance=self.inheritance,
            decorators=self.decorators,
            attributes=self.attributes,
            methods=methods,
        )
