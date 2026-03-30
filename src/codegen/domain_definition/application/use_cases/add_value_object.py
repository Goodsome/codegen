from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.value_object_spec import ValueObjectSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddValueObjectCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddValueObjectResult(BaseModel):
    success: bool


@dataclass
class AddValueObject:
    storage: BlueprintStorage

    def execute(self, cmd: AddValueObjectCommand) -> AddValueObjectResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        value_object = ValueObjectSpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )
        context.domain.add_value_object(value_object)

        self.storage.save(blueprint)

        return AddValueObjectResult(success=True)
