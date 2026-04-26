from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveRepositoryCommand(BaseModel):
    context_name: str
    name: str


class RemoveRepositoryResult(BaseModel):
    success: bool


@dataclass
class RemoveRepository:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveRepositoryCommand) -> RemoveRepositoryResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_repository(cmd.name)
        self.storage.save(blueprint)

        return RemoveRepositoryResult(success=True)
