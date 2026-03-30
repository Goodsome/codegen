from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveEntityCommand(BaseModel):
    context_name: str
    name: str


class RemoveEntityResult(BaseModel):
    success: bool


@dataclass
class RemoveEntity:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveEntityCommand) -> RemoveEntityResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_entity(cmd.name)

        self.storage.save(blueprint)

        return RemoveEntityResult(success=True)
