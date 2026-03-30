from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateUseCaseCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateUseCaseResult(BaseModel):
    success: bool


@dataclass
class UpdateUseCase:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateUseCaseCommand) -> UpdateUseCaseResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.application.get_use_case(cmd.name)

        existing.update(description=cmd.description)

        context.application.update_use_case(existing)
        self.storage.save(blueprint)

        return UpdateUseCaseResult(success=True)
