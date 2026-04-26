from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateDomainExceptionCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateDomainExceptionResult(BaseModel):
    success: bool


@dataclass
class UpdateDomainException:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateDomainExceptionCommand) -> UpdateDomainExceptionResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_domain_exception(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_domain_exception(existing)
        self.storage.save(blueprint)

        return UpdateDomainExceptionResult(success=True)
