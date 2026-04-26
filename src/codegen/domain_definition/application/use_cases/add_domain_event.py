from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.domain_event_spec import DomainEventSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddDomainEventCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddDomainEventResult(BaseModel):
    success: bool


@dataclass
class AddDomainEvent:
    storage: BlueprintStorage

    def execute(self, cmd: AddDomainEventCommand) -> AddDomainEventResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        domain_event = DomainEventSpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )

        context.domain.add_domain_event(domain_event)
        self.storage.save(blueprint)

        return AddDomainEventResult(success=True)
