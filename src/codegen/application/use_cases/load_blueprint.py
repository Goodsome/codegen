from dataclasses import dataclass

from codegen.domain.aggregates.blueprint import Blueprint
from codegen.domain.ports.blueprint_loader_port import BlueprintLoaderPort


@dataclass(frozen=True)
class LoadBlueprintCommand:
    """Command/Query for LoadBlueprint."""

    node: str | None = None


@dataclass(frozen=True)
class LoadBlueprintResult:
    """Result of LoadBlueprint."""

    blueprint: Blueprint | None


@dataclass
class LoadBlueprintHandler:
    """Handler for LoadBlueprint (command)."""

    blueprint_loader: BlueprintLoaderPort

    def execute(self, cmd: LoadBlueprintCommand) -> LoadBlueprintResult:

        blueprint = self.blueprint_loader.load("codegen.yaml")
        return LoadBlueprintResult(blueprint=blueprint)
