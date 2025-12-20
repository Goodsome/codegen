"""
Kind: ValueObject
Name: MethodSpec
Description: Standard specification for a class method.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from codegen.domain.value_objects.method_output import MethodOutput

from typing import List
from pydantic import Field


class MethodSpec(ValueObject):
    """Standard specification for a class method."""

    name: str

    description: str = Field(default="")

    inputs: List[Attribute]

    output: MethodOutput
