"""
Kind: ValueObject
Name: FunctionSpec
Description: Represents a function in a Python module.
"""

from codegen.shared.domain.value_objects.snake_string import SnakeString


from codegen.python_gen.domain.enums import FunctionType
from pydantic import Field

from codegen.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class FunctionSpec(ValueObject):
    """Represents a function in a Python module."""

    name: SnakeString
    decorators: list[str] = Field(default_factory=list)
    parameters: list[ParameterSpec] = Field(default_factory=list)
    return_annotation: TypeAnnotationSpec
    suite: str = Field(default="")
    function_type: FunctionType = Field(default=FunctionType.FUNCTION)
    is_private: bool = False

    @classmethod
    def create(
        cls,
        name: str,
        return_annotation: TypeAnnotationSpec,
        decorators: list[str] | None = None,
        parameters: list[ParameterSpec] | None = None,
        suite: str = "",
        function_type: FunctionType = FunctionType.FUNCTION,
        is_private: bool = False,
    ):
        return cls(
            name=SnakeString(name),
            decorators=decorators or [],
            parameters=parameters or [],
            suite=suite,
            return_annotation=return_annotation,
            function_type=function_type,
            is_private=is_private,
        )



    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        types.update(self.return_annotation.get_all_referenced_names())
        types.update(self.decorators)
        for p in self.parameters:
            types.update(p.annotation.get_all_referenced_names())
        return types

    def is_instance_method(self) -> bool:
        return self.function_type == FunctionType.INSTANCE_METHOD

    def merge(self, other: "FunctionSpec") -> "FunctionSpec":
        if self.name != other.name:
            return self
        suite = self.suite
        if not suite or suite == "...":
            suite = other.suite
        return self.__class__.create(
            name=self.name,
            decorators=self.decorators,
            parameters=self.parameters,
            suite=suite,
            return_annotation=self.return_annotation,
            function_type=self.function_type,
            is_private=self.is_private,
        )

    def is_init_method(self) -> bool:
        return self.name == "__init__"
