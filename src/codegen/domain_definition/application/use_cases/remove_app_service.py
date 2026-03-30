from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveAppServiceCommand(BaseModel):
    context_name: str
    name: str


class RemoveAppServiceResult(BaseModel):
    success: bool


@dataclass
class RemoveAppService:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveAppServiceCommand) -> RemoveAppServiceResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.application.remove_service(cmd.name)

        self.storage.save(blueprint)

        return RemoveAppServiceResult(success=True)
