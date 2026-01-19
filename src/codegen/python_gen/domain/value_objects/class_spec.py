"""
Kind: ValueObject
Name: ClassSpec
Description: Represents a class in a Python module.
"""

import ast

from pydantic.fields import Field

from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.shared.domain.value_objects.naming_string import PascalString
from codegen.shared.models import ValueObject


class ClassSpec(ValueObject):
    """Represents a class in a Python module."""

    name: PascalString
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
    ) -> "ClassSpec":
        return cls(
            name=PascalString(name),
            description=description,
            decorators=decorators or [],
            inheritance=inheritance or [],
            attributes=attributes or [],
            methods=methods or [],
        )

    @classmethod
    def create_value_object(cls) -> "ClassSpec":
        return cls.create(
            name="ValueObject",
            inheritance=["BaseModel"],
        )

    @classmethod
    def create_aggregate(cls) -> "ClassSpec":
        return cls.create(
            name="Aggregate",
            inheritance=["BaseModel"],
        )
    
    @classmethod
    def create_entity(cls) -> "ClassSpec":
        return cls.create(
            name="Entity",
            inheritance=["BaseModel"],
        )

    @classmethod
    def parse_ast(cls, node: ast.ClassDef, source_code: str):
        methods: list[FunctionSpec] = []
        attributes: list[ParameterSpec] = []
        inheritance: list[str] = [ast.unparse(base) for base in node.bases]
        decorators: list[str] = [
            ast.unparse(decorator) for decorator in node.decorator_list
        ]
        description: str = ast.get_docstring(node) or ""
        in_pydantic_model = False
        if (
            "ValueObject" in inheritance
            or "AggregateRoot" in inheritance
            or "BaseModel" in inheritance
        ):
            in_pydantic_model = True

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(FunctionSpec.parse_ast(item, source_code))
            elif isinstance(item, (ast.AnnAssign, ast.Assign)):
                attributes.extend(
                    ParameterSpec.parse_ast(
                        item,
                        in_pydantic_model=in_pydantic_model,
                    )
                )

        return cls.create(
            name=node.name,
            description=description,
            inheritance=inheritance,
            decorators=decorators,
            attributes=attributes,
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
