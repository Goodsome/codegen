from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveDomainPortCommand(BaseModel):
    context_name: str
    name: str


class RemoveDomainPortResult(BaseModel):
    success: bool


@dataclass
class RemoveDomainPort:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveDomainPortCommand) -> RemoveDomainPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_port(cmd.name)

        self.storage.save(blueprint)

        return RemoveDomainPortResult(success=True)
