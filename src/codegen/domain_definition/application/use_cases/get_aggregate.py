from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetAggregateQuery(BaseModel):
    context_name: str
    name: str


class GetAggregateResult(BaseModel):
    aggregate: AggregateSpec


@dataclass
class GetAggregate:
    storage: BlueprintStorage

    def execute(self, query: GetAggregateQuery) -> GetAggregateResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        aggregate = context.domain.get_aggregate(query.name)

        return GetAggregateResult(aggregate=aggregate)
