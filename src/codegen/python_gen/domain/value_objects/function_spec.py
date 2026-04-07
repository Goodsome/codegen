"""
Kind: ValueObject
Name: FunctionSpec
Description: Represents a function in a Python module.
"""

from typing import Self
from codegen.shared.domain.value_objects.snake_string import SnakeString


from codegen.python_gen.domain.enums import FunctionType
from pydantic import Field, model_validator

from codegen.shared.domain.core import ValueObject

from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class FunctionSpec(ValueObject):
    """Represents a function in a Python module."""

    name: SnakeString
    decorators: list[str] = Field(default_factory=list)
    parameters: list[VariableSpec] = Field(default_factory=list)
    return_annotation: TypeAnnotationSpec
    suite: str = Field(default="")
    function_type: FunctionType = Field(default=FunctionType.FUNCTION)
    description: str | None = None

    @model_validator(mode='after')
    def validate_parameter_order(self) -> Self:
        seen_default = False
        for param in self.parameters:
            if param.assignment is not None:
                seen_default = True
            elif seen_default:
                raise ValueError(
                    f"函数 '{self.name}' 参数顺序不合法: "
                    f"非默认参数 '{param.name}' 不能跟在默认参数之后。"
                )
        return self

    @classmethod
    def create(
        cls,
        name: str,
        return_annotation: TypeAnnotationSpec,
        decorators: list[str] | None = None,
        parameters: list[VariableSpec] | None = None,
        suite: str = "",
        function_type: FunctionType = FunctionType.FUNCTION,
        description: str | None = None,
    ):
        return cls(
            name=SnakeString(name),
            decorators=decorators or [],
            parameters=parameters or [],
            suite=suite,
            return_annotation=return_annotation,
            function_type=function_type,
            description=description,
        )

    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        types.update(self.return_annotation.get_all_referenced_names())
        for d in self.decorators:
            types.add(d.split(".")[0])
        for p in self.parameters:
            if p.type_spec:
                types.update(p.type_spec.get_all_referenced_names())
            if p.assignment:
                types.update(p.assignment.get_required_types())
        return types

    def is_instance_method(self) -> bool:
        return self.function_type == FunctionType.INSTANCE_METHOD

    def merge(self, other: "FunctionSpec") -> "FunctionSpec":
        if self.name != other.name:
            return self
        suite = self.suite
        if not suite or suite == "...":
            suite = other.suite
        description = self.description or other.description
        return self.__class__.create(
            name=self.name,
            decorators=self.decorators,
            parameters=self.parameters,
            suite=suite,
            return_annotation=self.return_annotation,
            function_type=self.function_type,
            description=description,
        )

    def is_init_method(self) -> bool:
        return self.name == "__init__"
