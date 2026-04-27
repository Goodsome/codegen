from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class AddAppPortCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddAppPortResult(BaseModel):
    success: bool


@dataclass
class AddAppPort:
    storage: BlueprintStorage

    def execute(self, cmd: AddAppPortCommand) -> AddAppPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        port = PortSpec.create(
            name=cmd.name,
            description=cmd.description,
        )
        context.application.add_port(port)

        self.storage.save(blueprint)

        return AddAppPortResult(success=True)
