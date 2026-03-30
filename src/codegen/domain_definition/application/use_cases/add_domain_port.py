from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class AddDomainPortCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddDomainPortResult(BaseModel):
    success: bool


@dataclass
class AddDomainPort:
    storage: BlueprintStorage

    def execute(self, cmd: AddDomainPortCommand) -> AddDomainPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        port = PortSpec.create(
            name=cmd.name,
            kind="adapter",
            description=cmd.description,
        )
        context.domain.add_port(port)

        self.storage.save(blueprint)

        return AddDomainPortResult(success=True)
