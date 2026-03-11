from pydantic import Field

from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec


class McpInterfaceSpec(ValueObject):
    """MCP 接口层规范"""

    tools: list[McpToolSpec] = Field(default_factory=list)