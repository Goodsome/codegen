"""
Kind: ValueObject
Name: MetaUseCaseResult
Description: Specification of a use case result to be generated.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class MetaUseCaseResult(ValueObject):
    """Specification of a use case result to be generated."""

    name: str

    attributes: List[Attribute]
