from pydantic import Field

from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.cli_command_spec import CliCommandSpec


class CliInterfaceSpec(ValueObject):
    """CLI 接口层规范"""

    commands: list[CliCommandSpec] = Field(default_factory=list)