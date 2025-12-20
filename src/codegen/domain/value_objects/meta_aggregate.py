"""
Kind: ValueObject
Name: MetaAggregate
Description: Specification of a domain aggregate to be generated.
"""
from pydantic import Field

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from codegen.domain.value_objects.method_spec import MethodSpec

from typing import List


class MetaAggregate(ValueObject):
    """Specification of a domain aggregate to be generated."""

    name: str

    description: str = Field(default="")

    attributes: List[Attribute]

    behaviors: List[MethodSpec] = Field(default_factory=list)
