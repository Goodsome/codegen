from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateMcpToolCommand(BaseModel):
    context_name: str
    name: str
    use_case: str | None = Field(default=None)
    description: str | None = Field(default=None)


class UpdateMcpToolResult(BaseModel):
    success: bool


@dataclass
class UpdateMcpTool:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateMcpToolCommand) -> UpdateMcpToolResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.interfaces.get_mcp_tool(cmd.name)

        existing.update(use_case=cmd.use_case, description=cmd.description)

        context.interfaces.update_mcp_tool(existing)
        self.storage.save(blueprint)

        return UpdateMcpToolResult(success=True)
