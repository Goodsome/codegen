from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.value_object_spec import ValueObjectSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetValueObjectQuery(BaseModel):
    context_name: str
    name: str


class GetValueObjectResult(BaseModel):
    value_object: ValueObjectSpec


@dataclass
class GetValueObject:
    storage: BlueprintStorage

    def execute(self, query: GetValueObjectQuery) -> GetValueObjectResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        value_object = context.domain.get_value_object(query.name)

        return GetValueObjectResult(value_object=value_object)
