"""
Kind: ValueObject
Name: Service
Description: Domain service specification (meta-model).
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.operation import Operation

from typing import List


class Service(ValueObject):
    """Domain service specification (meta-model)."""

    name: str

    description: str

    operations: List[Operation]
