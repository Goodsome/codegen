"""
Kind: ValueObject
Name: FunctionSpec
Description: Represents a function in a Python module.
"""

from pydantic import Field
from enum import StrEnum

from codegen.domain.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class FunctionType(StrEnum):
    CLASS_METHOD = "class_method"
    STATIC_METHOD = "static_method"
    INSTANCE_METHOD = "instance_method"
    FUNCTION = "function"


class FunctionSpec(ValueObject):
    """Represents a function in a Python module."""

    name: str
    decorators: list[str] = Field(default_factory=list)
    parameters: list[ParameterSpec] = Field(default_factory=list)
    return_annotation: TypeAnnotationSpec
    suite: str = Field(default="")
    function_type: FunctionType = Field(default=FunctionType.FUNCTION)

    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        types.update(self.return_annotation.get_all_referenced_names())
        for p in self.parameters:
            types.update(p.annotation.get_all_referenced_names())
        return types

    def is_instance_method(self) -> bool:
        return self.function_type == FunctionType.INSTANCE_METHOD
