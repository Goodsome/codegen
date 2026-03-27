"""
Kind: ValueObject
Name: FunctionSpec
Description: Represents a function in a Python module.
"""

from codegen.shared.domain.value_objects.snake_string import SnakeString


from codegen.python_gen.domain.enums import FunctionType
from pydantic import Field

from codegen.shared.models import ValueObject

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
    is_private: bool = False
    description: str | None = None

    @classmethod
    def create(
        cls,
        name: str,
        return_annotation: TypeAnnotationSpec,
        decorators: list[str] | None = None,
        parameters: list[VariableSpec] | None = None,
        suite: str = "",
        function_type: FunctionType = FunctionType.FUNCTION,
        is_private: bool = False,
        description: str | None = None,
    ):
        return cls(
            name=SnakeString(name),
            decorators=decorators or [],
            parameters=parameters or [],
            suite=suite,
            return_annotation=return_annotation,
            function_type=function_type,
            is_private=is_private,
            description=description,
        )



    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        types.update(self.return_annotation.get_all_referenced_names())
        types.update(self.decorators)
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
            is_private=self.is_private,
            description=description,
        )

    def is_init_method(self) -> bool:
        return self.name == "__init__"
