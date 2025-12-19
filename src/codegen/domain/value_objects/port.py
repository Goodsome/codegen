"""
Kind: ValueObject
Name: Port
Description: Domain port specification (meta-model).
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.operation import Operation

from typing import List


class Port(ValueObject):
    """Domain port specification (meta-model)."""

    name: str

    description: str

    kind: str

    operations: List[Operation]
