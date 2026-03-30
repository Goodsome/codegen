from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.implementation_spec import (
    ImplementationSpec,
)
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class AddImplementationCommand(BaseModel):
    context_name: str
    name: str
    implements: str
    technology: str
    description: str


class AddImplementationResult(BaseModel):
    success: bool


@dataclass
class AddImplementation:
    storage: BlueprintStorage

    def execute(self, cmd: AddImplementationCommand) -> AddImplementationResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        implementation = ImplementationSpec.create(
            name=cmd.name,
            implements=cmd.implements,
            technology=cmd.technology,
            description=cmd.description,
        )
        context.infrastructure.add_implementation(implementation)

        self.storage.save(blueprint)

        return AddImplementationResult(success=True)
