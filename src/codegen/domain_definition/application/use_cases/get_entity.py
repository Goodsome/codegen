from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.entity_spec import EntitySpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetEntityQuery(BaseModel):
    context_name: str
    name: str


class GetEntityResult(BaseModel):
    entity: EntitySpec


@dataclass
class GetEntity:
    storage: BlueprintStorage

    def execute(self, query: GetEntityQuery) -> GetEntityResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        entity = context.domain.get_entity(query.name)

        return GetEntityResult(entity=entity)
