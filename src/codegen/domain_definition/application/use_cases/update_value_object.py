from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateValueObjectCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateValueObjectResult(BaseModel):
    success: bool


@dataclass
class UpdateValueObject:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateValueObjectCommand) -> UpdateValueObjectResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_value_object(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_value_object(existing)
        self.storage.save(blueprint)

        return UpdateValueObjectResult(success=True)
