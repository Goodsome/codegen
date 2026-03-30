from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateEnumCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateEnumResult(BaseModel):
    success: bool


@dataclass
class UpdateEnum:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateEnumCommand) -> UpdateEnumResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_enum(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_enum(existing)
        self.storage.save(blueprint)

        return UpdateEnumResult(success=True)
