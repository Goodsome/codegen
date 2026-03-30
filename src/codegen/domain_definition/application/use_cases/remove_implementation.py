from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveImplementationCommand(BaseModel):
    context_name: str
    name: str


class RemoveImplementationResult(BaseModel):
    success: bool


@dataclass
class RemoveImplementation:
    storage: BlueprintStorage

    def execute(
        self, cmd: RemoveImplementationCommand
    ) -> RemoveImplementationResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.infrastructure.remove_implementation(cmd.name)

        self.storage.save(blueprint)

        return RemoveImplementationResult(success=True)
