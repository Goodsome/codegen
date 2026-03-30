from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateAppServiceCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateAppServiceResult(BaseModel):
    success: bool


@dataclass
class UpdateAppService:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateAppServiceCommand) -> UpdateAppServiceResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.application.get_service(cmd.name)

        existing.update(description=cmd.description)

        context.application.update_service(existing)
        self.storage.save(blueprint)

        return UpdateAppServiceResult(success=True)
