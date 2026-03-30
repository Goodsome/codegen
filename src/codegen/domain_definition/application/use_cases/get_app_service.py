from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetAppServiceQuery(BaseModel):
    context_name: str
    name: str


class GetAppServiceResult(BaseModel):
    service: ServiceSpec


@dataclass
class GetAppService:
    storage: BlueprintStorage

    def execute(self, query: GetAppServiceQuery) -> GetAppServiceResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        service = context.application.get_service(query.name)

        return GetAppServiceResult(service=service)
