from pydantic import Field

from codegen.domain_definition.domain.value_objects.port_binding import PortBinding
from codegen.shared.models import ValueObject


class ContainerSpec(ValueObject):
    """Specification for a container (dependency injection)."""

    bindings: list[PortBinding] = Field(default_factory=list)
