from pydantic import Field

from codegen.shared.models import ValueObject


class CliCommandSpec(ValueObject):
    """CLI 命令规范"""

    name: str
    use_case: str
    description: str = Field(default_factory=str)