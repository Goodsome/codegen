from dataclasses import dataclass

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage


class UpdateAggregateCommand(BaseModel):
    context_name: str
    name: str
    description: str | None = Field(default=None)


class UpdateAggregateResult(BaseModel):
    success: bool


@dataclass
class UpdateAggregate:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateAggregateCommand) -> UpdateAggregateResult:
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        context = blueprint.get_context(cmd.context_name)
        existing = context.domain.get_aggregate(cmd.name)

        existing.update(description=cmd.description)

        context.domain.update_aggregate(existing)
        self.storage.save(blueprint)

        return UpdateAggregateResult(success=True)
