from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.cli_command_spec import (
    CliCommandSpec,
)
from codegen.shared.domain.value_objects.kebab_string import KebabString


class GetCliCommandQuery(BaseModel):
    context_name: str
    name: str


class GetCliCommandResult(BaseModel):
    cli_command: CliCommandSpec


@dataclass
class GetCliCommand:
    storage: BlueprintStorage

    def execute(self, query: GetCliCommandQuery) -> GetCliCommandResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        cli_command = context.interfaces.get_cli_command(KebabString(query.name))

        return GetCliCommandResult(cli_command=cli_command)
