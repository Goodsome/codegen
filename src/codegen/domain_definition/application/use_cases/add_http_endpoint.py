from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.http_endpoint_spec import (
    HttpEndpointSpec,
)


class AddHttpEndpointCommand(BaseModel):
    context_name: str
    path: str
    method: str
    use_case: str
    description: str


class AddHttpEndpointResult(BaseModel):
    success: bool


@dataclass
class AddHttpEndpoint:
    storage: BlueprintStorage

    def execute(self, cmd: AddHttpEndpointCommand) -> AddHttpEndpointResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)

        http_endpoint = HttpEndpointSpec(
            path=cmd.path,
            method=cmd.method,
            use_case=cmd.use_case,
            description=cmd.description,
        )
        context.interfaces.add_http_endpoint(http_endpoint)

        self.storage.save(blueprint)

        return AddHttpEndpointResult(success=True)
