from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveDomainExceptionCommand(BaseModel):
    context_name: str
    name: str


class RemoveDomainExceptionResult(BaseModel):
    success: bool


@dataclass
class RemoveDomainException:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveDomainExceptionCommand) -> RemoveDomainExceptionResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_domain_exception(cmd.name)
        self.storage.save(blueprint)

        return RemoveDomainExceptionResult(success=True)
