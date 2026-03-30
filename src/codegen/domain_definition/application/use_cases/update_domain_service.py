from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateDomainServiceCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateDomainServiceResult(BaseModel):
    success: bool


@dataclass
class UpdateDomainService:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateDomainServiceCommand) -> UpdateDomainServiceResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_service(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_service(existing)
        self.storage.save(blueprint)

        return UpdateDomainServiceResult(success=True)
