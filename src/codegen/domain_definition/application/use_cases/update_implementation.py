from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateImplementationCommand(BaseModel):
    context_name: str
    name: str
    implements: str | None = Field(default=None)
    technology: str | None = Field(default=None)
    description: str | None = Field(default=None)


class UpdateImplementationResult(BaseModel):
    success: bool


@dataclass
class UpdateImplementation:
    storage: BlueprintStorage

    def execute(
        self, cmd: UpdateImplementationCommand
    ) -> UpdateImplementationResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.infrastructure.get_implementation(cmd.name)

        existing.update(implements=cmd.implements, technology=cmd.technology, description=cmd.description)

        context.infrastructure.update_implementation(existing)
        self.storage.save(blueprint)

        return UpdateImplementationResult(success=True)
