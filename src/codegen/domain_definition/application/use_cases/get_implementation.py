from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.implementation_spec import (
    ImplementationSpec,
)
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetImplementationQuery(BaseModel):
    context_name: str
    name: str


class GetImplementationResult(BaseModel):
    implementation: ImplementationSpec


@dataclass
class GetImplementation:
    storage: BlueprintStorage

    def execute(self, query: GetImplementationQuery) -> GetImplementationResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        implementation = context.infrastructure.get_implementation(query.name)

        return GetImplementationResult(implementation=implementation)
