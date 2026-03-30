from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.kebab_string import KebabString


class RemoveCliCommandCommand(BaseModel):
    context_name: str
    name: str


class RemoveCliCommandResult(BaseModel):
    success: bool


@dataclass
class RemoveCliCommand:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveCliCommandCommand) -> RemoveCliCommandResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.interfaces.remove_cli_command(KebabString(cmd.name))

        self.storage.save(blueprint)

        return RemoveCliCommandResult(success=True)
