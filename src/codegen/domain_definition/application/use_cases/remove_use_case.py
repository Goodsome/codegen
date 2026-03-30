from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveUseCaseCommand(BaseModel):
    context_name: str
    name: str


class RemoveUseCaseResult(BaseModel):
    success: bool


@dataclass
class RemoveUseCase:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveUseCaseCommand) -> RemoveUseCaseResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.application.remove_use_case(cmd.name)

        self.storage.save(blueprint)

        return RemoveUseCaseResult(success=True)
