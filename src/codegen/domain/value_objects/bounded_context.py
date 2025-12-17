"""
Kind: ValueObject
Name: BoundedContext
Description: A logical boundary within the system.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.aggregate import Aggregate

from codegen.domain.value_objects.value_spec import ValueSpec

from typing import List


class BoundedContext(ValueObject):
    """A logical boundary within the system."""

    name: str

    description: str

    aggregates: List[Aggregate]

    value_objects: List[ValueSpec]
