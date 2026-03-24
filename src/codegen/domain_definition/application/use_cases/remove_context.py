from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from dataclasses import dataclass
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from pydantic import BaseModel


class RemoveContextCommand(BaseModel):
    name: str


class RemoveContextResult(BaseModel):
    blueprint: Blueprint


@dataclass
class RemoveContext:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveContextCommand) -> RemoveContextResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        updated = blueprint.remove_context(name=cmd.name)
        self.storage.save(updated)

        return RemoveContextResult(blueprint=updated)
