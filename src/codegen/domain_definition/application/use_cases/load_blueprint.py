from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from dataclasses import dataclass
from typing import Self
from codegen.domain_definition.application.dtos.load_blueprint_command import (
    LoadBlueprintCommand,
)
from codegen.domain_definition.application.dtos.load_blueprint_result import (
    LoadBlueprintResult,
)


@dataclass
class LoadBlueprint:
    """Loads the blueprint from a file."""

    blueprint_loader: BlueprintStorage

    def execute(self: Self, cmd: LoadBlueprintCommand) -> LoadBlueprintResult:
        blueprint = self.blueprint_loader.load()
        if blueprint is None:
            raise ValueError("Failed to load blueprint")
        return LoadBlueprintResult(blueprint=blueprint)
