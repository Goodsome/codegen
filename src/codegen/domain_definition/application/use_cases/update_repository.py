from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateRepositoryCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateRepositoryResult(BaseModel):
    success: bool


@dataclass
class UpdateRepository:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateRepositoryCommand) -> UpdateRepositoryResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_repository(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_repository(existing)
        self.storage.save(blueprint)

        return UpdateRepositoryResult(success=True)
