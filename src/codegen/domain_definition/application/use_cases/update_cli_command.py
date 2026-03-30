from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateCliCommandCommand(BaseModel):
    context_name: str
    name: str
    use_case: str | None = Field(default=None)
    description: str | None = Field(default=None)


class UpdateCliCommandResult(BaseModel):
    success: bool


@dataclass
class UpdateCliCommand:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateCliCommandCommand) -> UpdateCliCommandResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.interfaces.get_cli_command(cmd.name)

        existing.update(use_case=cmd.use_case, description=cmd.description)

        context.interfaces.update_cli_command(existing)
        self.storage.save(blueprint)

        return UpdateCliCommandResult(success=True)
