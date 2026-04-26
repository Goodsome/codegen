from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.domain_exception_spec import (
    DomainExceptionSpec,
)
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddDomainExceptionCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddDomainExceptionResult(BaseModel):
    success: bool


@dataclass
class AddDomainException:
    storage: BlueprintStorage

    def execute(self, cmd: AddDomainExceptionCommand) -> AddDomainExceptionResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        domain_exception = DomainExceptionSpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )

        context.domain.add_domain_exception(domain_exception)
        self.storage.save(blueprint)

        return AddDomainExceptionResult(success=True)
