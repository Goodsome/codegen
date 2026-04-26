from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.domain_exception_spec import (
    DomainExceptionSpec,
)
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class GetDomainExceptionQuery(BaseModel):
    context_name: str
    name: str


class GetDomainExceptionResult(BaseModel):
    domain_exception: DomainExceptionSpec


@dataclass
class GetDomainException:
    storage: BlueprintStorage

    def execute(self, query: GetDomainExceptionQuery) -> GetDomainExceptionResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(query.context_name)
        domain_exception = context.domain.get_domain_exception(query.name)

        return GetDomainExceptionResult(domain_exception=domain_exception)
