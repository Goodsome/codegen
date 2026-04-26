from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.repository_spec import RepositorySpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddRepositoryCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddRepositoryResult(BaseModel):
    success: bool


@dataclass
class AddRepository:
    storage: BlueprintStorage

    def execute(self, cmd: AddRepositoryCommand) -> AddRepositoryResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        repository = RepositorySpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )

        context.domain.add_repository(repository)
        self.storage.save(blueprint)

        return AddRepositoryResult(success=True)
