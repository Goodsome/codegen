from pydantic import Field

from codegen.shared.models import ValueObject


class McpToolSpec(ValueObject):
    """MCP Tool 规范"""

    name: str
    use_case: str
    description: str = Field(default_factory=str)