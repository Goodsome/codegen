"""
Kind: ValueObject
Name: ClassSpec
Description: Represents a class in a Python module.
"""

from pydantic.fields import Field
from codegen.domain.shared.models import ValueObject

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
