from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.entity_spec import EntitySpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddEntityCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddEntityResult(BaseModel):
    success: bool


@dataclass
class AddEntity:
    storage: BlueprintStorage

    def execute(self, cmd: AddEntityCommand) -> AddEntityResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        entity = EntitySpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )
        context.domain.add_entity(entity)

        self.storage.save(blueprint)

        return AddEntityResult(success=True)
