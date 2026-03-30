from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class RemoveAggregateCommand(BaseModel):
    context_name: str
    name: str


class RemoveAggregateResult(BaseModel):
    success: bool


@dataclass
class RemoveAggregate:
    storage: BlueprintStorage

    def execute(self, cmd: RemoveAggregateCommand) -> RemoveAggregateResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        context.domain.remove_aggregate(cmd.name)

        self.storage.save(blueprint)

        return RemoveAggregateResult(success=True)
