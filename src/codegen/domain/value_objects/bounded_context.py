"""
Kind: ValueObject
Name: BoundedContext
Description: A logical boundary within the system.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.aggregate import Aggregate

from codegen.domain.value_objects.port import Port

from codegen.domain.value_objects.service import Service

from codegen.domain.value_objects.use_case import UseCase

from codegen.domain.value_objects.value_spec import ValueSpec

from typing import List


class BoundedContext(ValueObject):
    """A logical boundary within the system."""

    name: str

    description: str

    aggregates: List[Aggregate]

    value_objects: List[ValueSpec]

    services: List[Service]

    ports: List[Port]

    use_cases: List[UseCase]
