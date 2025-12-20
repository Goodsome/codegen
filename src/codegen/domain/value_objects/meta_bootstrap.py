"""
Kind: ValueObject
Name: MetaBootstrap
Description: Specification of the bootstrap configuration.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.port_binding import PortBinding

from typing import List


class MetaBootstrap(ValueObject):
    """Specification of the bootstrap configuration."""

    bindings: List[PortBinding]
