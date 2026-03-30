from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddDomainServiceCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddDomainServiceResult(BaseModel):
    success: bool


@dataclass
class AddDomainService:
    storage: BlueprintStorage

    def execute(self, cmd: AddDomainServiceCommand) -> AddDomainServiceResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        service = ServiceSpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )
        context.domain.add_service(service)

        self.storage.save(blueprint)

        return AddDomainServiceResult(success=True)
