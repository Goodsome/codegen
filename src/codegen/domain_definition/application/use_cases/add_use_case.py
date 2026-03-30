from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class AddUseCaseCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddUseCaseResult(BaseModel):
    success: bool


@dataclass
class AddUseCase:
    storage: BlueprintStorage

    def execute(self, cmd: AddUseCaseCommand) -> AddUseCaseResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        use_case = UseCaseSpec.create(
            name=cmd.name,
            kind="command",
            description=cmd.description,
        )
        context.application.add_use_case(use_case)

        self.storage.save(blueprint)

        return AddUseCaseResult(success=True)
