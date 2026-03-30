from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetDomainPortQuery(BaseModel):
    context_name: str
    name: str


class GetDomainPortResult(BaseModel):
    port: PortSpec


@dataclass
class GetDomainPort:
    storage: BlueprintStorage

    def execute(self, query: GetDomainPortQuery) -> GetDomainPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        port = context.domain.get_port(query.name)

        return GetDomainPortResult(port=port)
