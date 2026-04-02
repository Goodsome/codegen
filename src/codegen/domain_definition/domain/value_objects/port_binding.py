from codegen.shared.domain.core import ValueObject


class PortBinding(ValueObject):
    """Binding between a port and an adapter."""

    port: str
    implementation: str
