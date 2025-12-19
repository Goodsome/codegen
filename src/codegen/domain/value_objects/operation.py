"""
Kind: ValueObject
Name: Operation
Description: An operation of a Service/Port.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class Operation(ValueObject):
    """An operation of a Service/Port."""

    name: str

    description: str

    inputs: List[Attribute]

    output_type: str
