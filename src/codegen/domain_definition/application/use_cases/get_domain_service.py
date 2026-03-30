from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetDomainServiceQuery(BaseModel):
    context_name: str
    name: str


class GetDomainServiceResult(BaseModel):
    service: ServiceSpec


@dataclass
class GetDomainService:
    storage: BlueprintStorage

    def execute(self, query: GetDomainServiceQuery) -> GetDomainServiceResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        service = context.domain.get_service(query.name)

        return GetDomainServiceResult(service=service)
