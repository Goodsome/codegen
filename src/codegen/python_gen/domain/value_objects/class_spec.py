"""
Kind: ValueObject
Name: ClassSpec
Description: Represents a class in a Python module.
"""

import ast

from pydantic.fields import Field
from codegen.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec


class ClassSpec(ValueObject):
    """Represents a class in a Python module."""

    name: str
    description: str = Field(default="")
    decorators: list[str] = Field(default_factory=list)
    inheritance: list[str] = Field(default_factory=list)
    attributes: list[ParameterSpec] = Field(default_factory=list)
    methods: list[FunctionSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        decorators: list[str] | None = None,
        inheritance: list[str] | None = None,
        attributes: list[ParameterSpec] | None = None,
        methods: list[FunctionSpec] | None = None,
    ):
        return cls(
            name=name,
            description=description,
            decorators=decorators or [],
            inheritance=inheritance or [],
            attributes=attributes or [],
            methods=methods or [],
        )

    @classmethod
    def parse_ast(cls, node: ast.ClassDef, source_code: str):
        methods: list[FunctionSpec] = []
        inheritance: list[str] = [ast.unparse(base) for base in node.bases]
        decorators: list[str] = [
            ast.unparse(decorator) for decorator in node.decorator_list
        ]
        description: str = ast.get_docstring(node) or ""

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(FunctionSpec.parse_ast(item, source_code))

        return cls.create(
            name=node.name,
            description=description,
            inheritance=inheritance,
            decorators=decorators,
            methods=methods,
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
