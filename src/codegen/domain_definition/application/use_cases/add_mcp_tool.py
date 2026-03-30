from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.mcp_tool_spec import McpToolSpec


class AddMcpToolCommand(BaseModel):
    context_name: str
    name: str
    use_case: str
    description: str


class AddMcpToolResult(BaseModel):
    success: bool


@dataclass
class AddMcpTool:
    storage: BlueprintStorage

    def execute(self, cmd: AddMcpToolCommand) -> AddMcpToolResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        mcp_tool = McpToolSpec(
            name=cmd.name,
            use_case=cmd.use_case,
            description=cmd.description,
        )
        context.interfaces.add_mcp_tool(mcp_tool)

        self.storage.save(blueprint)

        return AddMcpToolResult(success=True)
