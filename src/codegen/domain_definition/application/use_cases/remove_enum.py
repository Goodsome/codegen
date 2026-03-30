from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveEnumCommand(BaseModel):
    context_name: str
    name: str


class RemoveEnumResult(BaseModel):
    success: bool


@dataclass
class RemoveEnum:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveEnumCommand) -> RemoveEnumResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_enum(cmd.name)

        self.storage.save(blueprint)

        return RemoveEnumResult(success=True)
