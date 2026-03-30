from dataclasses import dataclass

from pydantic import BaseModel

from codegen.domain_definition.domain.entities.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.shared.domain.value_objects.pascal_string import PascalString


class AddAggregateCommand(BaseModel):
    context_name: str
    name: str
    description: str


class AddAggregateResult(BaseModel):
    success: bool


@dataclass
class AddAggregate:
    storage: BlueprintStorage

    def execute(self, cmd: AddAggregateCommand) -> AddAggregateResult:
        # Load current blueprint
        blueprint = self.storage.load()
        if blueprint is None:
            raise ValueError("Blueprint not loaded")

        # Get context by name
        context = blueprint.get_context(cmd.context_name)

        # Create aggregate
        aggregate = AggregateSpec(
            name=PascalString(cmd.name),
            description=cmd.description,
        )

        # Add aggregate to domain
        context.domain.add_aggregate(aggregate)

        # Save the updated blueprint
        self.storage.save(blueprint)

        return AddAggregateResult(success=True)
