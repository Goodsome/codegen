"""
Kind: ValueObject
Name: FunctionSpec
Description: Represents a function in a Python module.
"""

from pydantic import Field

from codegen.domain.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class FunctionSpec(ValueObject):
    """Represents a function in a Python module."""

    name: str
    decorators: list[str] = Field(default_factory=list)
    parameters: list[ParameterSpec] = Field(default_factory=list)
    return_annotation: TypeAnnotationSpec
    suite: str = Field(default="")
