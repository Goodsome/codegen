from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.enum_spec import EnumSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddEnumCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddEnumResult(BaseModel):
    success: bool


@dataclass
class AddEnum:
    storage: BlueprintStorage

    def execute(self, cmd: AddEnumCommand) -> AddEnumResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        enum = EnumSpec(
            name=PascalString(cmd.name),
            description=cmd.description,
            members=[],
        )
        context.domain.add_enum(enum)

        self.storage.save(blueprint)

        return AddEnumResult(success=True)
