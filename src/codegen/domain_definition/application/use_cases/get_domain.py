from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.domain_spec import DomainSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetDomainQuery(BaseModel):
    context_name: str


class GetDomainResult(BaseModel):
    domain: DomainSpec


@dataclass
class GetDomain:
    storage: BlueprintStorage

    def execute(self, query: GetDomainQuery) -> GetDomainResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        return GetDomainResult(domain=context.domain)
