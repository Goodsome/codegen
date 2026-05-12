from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from codegen.domain_definition.domain.entities.bounded_context import BoundedContext
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from dataclasses import dataclass
from codegen.domain_definition.application.dtos.init_project_command import (
    InitProjectCommand,
)
from codegen.domain_definition.application.dtos.init_project_result import (
    InitProjectResult,
)
from typing import Self


@dataclass
class InitProject:
    """Initializes a new project blueprint with a default Shared context."""

    storage: BlueprintStorage

    def execute(self: Self, cmd: InitProjectCommand) -> InitProjectResult:
        project_name = cmd.project_name if cmd.project_name else "MyProject"
        shared_context = BoundedContext.create(name="Shared")
        blueprint = Blueprint.create(name=project_name, contexts=[shared_context])
        self.storage.save(blueprint)
        return InitProjectResult(blueprint=blueprint)
