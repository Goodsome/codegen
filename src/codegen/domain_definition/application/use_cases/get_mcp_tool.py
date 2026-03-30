from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec


class GetMcpToolQuery(BaseModel):
    context_name: str
    name: str


class GetMcpToolResult(BaseModel):
    mcp_tool: McpToolSpec


@dataclass
class GetMcpTool:
    storage: BlueprintStorage

    def execute(self, query: GetMcpToolQuery) -> GetMcpToolResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        mcp_tool = context.interfaces.get_mcp_tool(query.name)

        return GetMcpToolResult(mcp_tool=mcp_tool)
