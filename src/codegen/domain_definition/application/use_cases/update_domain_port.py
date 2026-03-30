from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateDomainPortCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateDomainPortResult(BaseModel):
    success: bool


@dataclass
class UpdateDomainPort:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateDomainPortCommand) -> UpdateDomainPortResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_port(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_port(existing)
        self.storage.save(blueprint)

        return UpdateDomainPortResult(success=True)
