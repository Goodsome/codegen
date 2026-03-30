from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateHttpEndpointCommand(BaseModel):
    context_name: str
    path: str
    method: str | None = Field(default=None)
    use_case: str | None = Field(default=None)
    description: str | None = Field(default=None)


class UpdateHttpEndpointResult(BaseModel):
    success: bool


@dataclass
class UpdateHttpEndpoint:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateHttpEndpointCommand) -> UpdateHttpEndpointResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.interfaces.get_http_endpoint(cmd.path)

        existing.update(method=cmd.method, use_case=cmd.use_case, description=cmd.description)

        context.interfaces.update_http_endpoint(existing)
        self.storage.save(blueprint)

        return UpdateHttpEndpointResult(success=True)
