from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveMcpToolCommand(BaseModel):
    context_name: str
    name: str


class RemoveMcpToolResult(BaseModel):
    success: bool


@dataclass
class RemoveMcpTool:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveMcpToolCommand) -> RemoveMcpToolResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.interfaces.remove_mcp_tool(cmd.name)

        self.storage.save(blueprint)

        return RemoveMcpToolResult(success=True)
