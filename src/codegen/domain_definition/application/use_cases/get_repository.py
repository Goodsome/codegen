from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.repository_spec import RepositorySpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetRepositoryQuery(BaseModel):
    context_name: str
    name: str


class GetRepositoryResult(BaseModel):
    repository: RepositorySpec


@dataclass
class GetRepository:
    storage: BlueprintStorage

    def execute(self, query: GetRepositoryQuery) -> GetRepositoryResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        repository = context.domain.get_repository(query.name)

        return GetRepositoryResult(repository=repository)
