from codegen.domain_definition.domain.aggregates.blueprint import Blueprint
from codegen.domain_definition.domain.entities.bounded_context import BoundedContext
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from pydantic import BaseModel
from dataclasses import dataclass


class InitProjectCommand(BaseModel):
    project_name: str | None = None
    project_description: str | None = None


class InitProjectResult(BaseModel):
    blueprint: Blueprint


@dataclass
class InitProject:
    """Initializes a new project blueprint with a default Shared context."""

    storage: BlueprintStorage

    def execute(self, cmd: InitProjectCommand) -> InitProjectResult:
        # Determine project name and description
        project_name = cmd.project_name if cmd.project_name else "MyProject"
        project_description = cmd.project_description if cmd.project_description else f"{project_name} project"

        # Create default Shared context
        shared_context = BoundedContext.create(
            name="Shared",
            description="Common generic components.",
        )

        # Create the blueprint
        blueprint = Blueprint.create(
            name=project_name,
            description=project_description,
            contexts=[shared_context],
        )

        # Save to storage
        self.storage.save(blueprint)

        return InitProjectResult(blueprint=blueprint)
