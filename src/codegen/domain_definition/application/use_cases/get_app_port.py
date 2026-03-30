from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetAppPortQuery(BaseModel):
    context_name: str
    name: str


class GetAppPortResult(BaseModel):
    port: PortSpec


@dataclass
class GetAppPort:
    storage: BlueprintStorage

    def execute(self, query: GetAppPortQuery) -> GetAppPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        port = context.application.get_port(query.name)

        return GetAppPortResult(port=port)
