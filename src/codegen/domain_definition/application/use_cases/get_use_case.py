from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetUseCaseQuery(BaseModel):
    context_name: str
    name: str


class GetUseCaseResult(BaseModel):
    use_case: UseCaseSpec


@dataclass
class GetUseCase:
    storage: BlueprintStorage

    def execute(self, query: GetUseCaseQuery) -> GetUseCaseResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        use_case = context.application.get_use_case(query.name)

        return GetUseCaseResult(use_case=use_case)
