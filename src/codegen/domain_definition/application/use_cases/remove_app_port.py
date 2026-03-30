from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveAppPortCommand(BaseModel):
    context_name: str
    name: str


class RemoveAppPortResult(BaseModel):
    success: bool


@dataclass
class RemoveAppPort:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveAppPortCommand) -> RemoveAppPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.application.remove_port(cmd.name)

        self.storage.save(blueprint)

        return RemoveAppPortResult(success=True)
