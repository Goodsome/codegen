"""
Kind: ValueObject
Name: PortBinding
Description: Binding between a port and an adapter.
"""

from codegen.domain.shared.models import ValueObject


class PortBinding(ValueObject):
    """Binding between a port and an adapter."""

    port: str

    implementation: str
