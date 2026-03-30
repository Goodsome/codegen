from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import (
    HttpEndpointSpec,
)


class GetHttpEndpointQuery(BaseModel):
    context_name: str
    path: str


class GetHttpEndpointResult(BaseModel):
    http_endpoint: HttpEndpointSpec


@dataclass
class GetHttpEndpoint:
    storage: BlueprintStorage

    def execute(self, query: GetHttpEndpointQuery) -> GetHttpEndpointResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        http_endpoint = context.interfaces.get_http_endpoint(query.path)

        return GetHttpEndpointResult(http_endpoint=http_endpoint)
