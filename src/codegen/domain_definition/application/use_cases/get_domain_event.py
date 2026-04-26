from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.domain_event_spec import DomainEventSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetDomainEventQuery(BaseModel):
    context_name: str
    name: str


class GetDomainEventResult(BaseModel):
    domain_event: DomainEventSpec


@dataclass
class GetDomainEvent:
    storage: BlueprintStorage

    def execute(self, query: GetDomainEventQuery) -> GetDomainEventResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        domain_event = context.domain.get_domain_event(query.name)

        return GetDomainEventResult(domain_event=domain_event)
