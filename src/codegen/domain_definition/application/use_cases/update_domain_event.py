from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateDomainEventCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateDomainEventResult(BaseModel):
    success: bool


@dataclass
class UpdateDomainEvent:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateDomainEventCommand) -> UpdateDomainEventResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_domain_event(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_domain_event(existing)
        self.storage.save(blueprint)

        return UpdateDomainEventResult(success=True)
