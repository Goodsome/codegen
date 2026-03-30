from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.cli_command_spec import (
    CliCommandSpec,
)
from codegen.shared.domain.value_objects.kebab_string import KebabString
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddCliCommandCommand(BaseModel):
    context_name: str
    name: str
    use_case: str
    description: str


class AddCliCommandResult(BaseModel):
    success: bool


@dataclass
class AddCliCommand:
    storage: BlueprintStorage

    def execute(self, cmd: AddCliCommandCommand) -> AddCliCommandResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        cli_command = CliCommandSpec(
            name=KebabString(cmd.name),
            use_case=PascalString(cmd.use_case),
            description=cmd.description,
        )
        context.interfaces.add_cli_command(cli_command)

        self.storage.save(blueprint)

        return AddCliCommandResult(success=True)
