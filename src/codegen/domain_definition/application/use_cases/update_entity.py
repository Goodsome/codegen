from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateEntityCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateEntityResult(BaseModel):
    success: bool


@dataclass
class UpdateEntity:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateEntityCommand) -> UpdateEntityResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_entity(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_entity(existing)
        self.storage.save(blueprint)

        return UpdateEntityResult(success=True)
