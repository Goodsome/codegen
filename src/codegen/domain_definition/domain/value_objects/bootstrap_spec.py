from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.config_spec import ConfigSpec
from codegen.domain_definition.domain.value_objects.container_spec import ContainerSpec


class BootstrapSpec(ValueObject):
    """Specification of the bootstrap configuration."""

    config: ConfigSpec | None = Field(default=None)
    container: ContainerSpec | None = Field(default=None)
