from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from dataclasses import dataclass
from pydantic import BaseModel


class UpsertContextCommand(BaseModel):
    name: str
    description: str


class UpsertContextResult(BaseModel):
    blueprint: Blueprint


@dataclass
class UpsertContext:
    storage: BlueprintStorage

    def execute(self, cmd: UpsertContextCommand) -> UpsertContextResult:
        # Load current blueprint
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        # Upsert the context
        updated = blueprint.upsert_context(name=cmd.name, description=cmd.description)

        # Save the updated blueprint
        self.storage.save(updated)

        return UpsertContextResult(blueprint=updated)
