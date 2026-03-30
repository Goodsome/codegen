from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddAppServiceCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddAppServiceResult(BaseModel):
    success: bool


@dataclass
class AddAppService:
    storage: BlueprintStorage

    def execute(self, cmd: AddAppServiceCommand) -> AddAppServiceResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        service = ServiceSpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )
        context.application.add_service(service)

        self.storage.save(blueprint)

        return AddAppServiceResult(success=True)
