from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveDomainEventCommand(BaseModel):
    context_name: str
    name: str


class RemoveDomainEventResult(BaseModel):
    success: bool


@dataclass
class RemoveDomainEvent:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveDomainEventCommand) -> RemoveDomainEventResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_domain_event(cmd.name)
        self.storage.save(blueprint)

        return RemoveDomainEventResult(success=True)
