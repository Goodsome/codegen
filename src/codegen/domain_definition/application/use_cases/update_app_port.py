from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateAppPortCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateAppPortResult(BaseModel):
    success: bool


@dataclass
class UpdateAppPort:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateAppPortCommand) -> UpdateAppPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.application.get_port(cmd.name)

        existing.update(description=cmd.description)

        context.application.update_port(existing)
        self.storage.save(blueprint)

        return UpdateAppPortResult(success=True)
