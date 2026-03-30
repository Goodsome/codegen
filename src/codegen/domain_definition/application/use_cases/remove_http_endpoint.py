from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveHttpEndpointCommand(BaseModel):
    context_name: str
    path: str


class RemoveHttpEndpointResult(BaseModel):
    success: bool


@dataclass
class RemoveHttpEndpoint:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveHttpEndpointCommand) -> RemoveHttpEndpointResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.interfaces.remove_http_endpoint(cmd.path)

        self.storage.save(blueprint)

        return RemoveHttpEndpointResult(success=True)
