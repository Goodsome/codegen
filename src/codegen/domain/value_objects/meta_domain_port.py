"""
Kind: ValueObject
Name: MetaDomainPort
Description: Specification of a domain port to be generated.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.method_spec import MethodSpec

from typing import List


class MetaDomainPort(ValueObject):
    """Specification of a domain port to be generated."""

    name: str

    description: str

    kind: str

    operations: List[MethodSpec]
