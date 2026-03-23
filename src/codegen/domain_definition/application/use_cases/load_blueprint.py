from codegen.domain_definition.domain.ports.blueprint_storage import (
    BlueprintStorage,
)
from dataclasses import dataclass
from codegen.domain_definition.domain.aggregates.blueprint import Blueprint


@dataclass(frozen=True)
class LoadBlueprintCommand:

    node: str | None = None


@dataclass(frozen=True)
class LoadBlueprintResult:

    blueprint: Blueprint


@dataclass
class LoadBlueprint:
    """Loads the blueprint from a file."""

    blueprint_loader: BlueprintStorage

    def execute(self, cmd: LoadBlueprintCommand) -> LoadBlueprintResult:
        blueprint = self.blueprint_loader.load()
        if blueprint is None:
            raise ValueError("Failed to load blueprint")
        return LoadBlueprintResult(blueprint=blueprint)
