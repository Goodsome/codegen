from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveValueObjectCommand(BaseModel):
    context_name: str
    name: str


class RemoveValueObjectResult(BaseModel):
    success: bool


@dataclass
class RemoveValueObject:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveValueObjectCommand) -> RemoveValueObjectResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_value_object(cmd.name)

        self.storage.save(blueprint)

        return RemoveValueObjectResult(success=True)
