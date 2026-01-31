from dataclasses import dataclass
from typing import Any

from codegen.domain_definition.domain.ports.blueprint_storage import BlueprintStorage
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)


@dataclass(frozen=True)
class AddComponentCommand:
    context: str
    component: Any  # Spec object (AggregateSpec, etc.) or BoundedContext (if context itself)


@dataclass
class AddComponent:
    storage: BlueprintStorage

    def execute(self, cmd: AddComponentCommand):
        blueprint = self.storage.load()
        if not blueprint:
            raise ValueError("Blueprint not found")

        if isinstance(cmd.component, BoundedContext):
            new_blueprint = blueprint.add_context(cmd.component)
        else:
            context = blueprint.get_context(cmd.context)
            if not context:
                raise ValueError(f"Context '{cmd.context}' not found")
            
            # Simplified logic: BoundedContext handles dispatch
            new_context = context.add_component(cmd.component)
            new_blueprint = blueprint.update_context(new_context)

        self.storage.save(new_blueprint)


@dataclass(frozen=True)
class UpdateComponentCommand:
    context: str
    component: Any


@dataclass
class UpdateComponent:
    storage: BlueprintStorage

    def execute(self, cmd: UpdateComponentCommand):
        blueprint = self.storage.load()
        if not blueprint:
            raise ValueError("Blueprint not found")
            
        if isinstance(cmd.component, BoundedContext):
             new_blueprint = blueprint.update_context(cmd.component)
        else:
            context = blueprint.get_context(cmd.context)
            if not context:
                raise ValueError(f"Context '{cmd.context}' not found")

            # Simplified logic: BoundedContext handles dispatch
            new_context = context.update_component(cmd.component)
            new_blueprint = blueprint.update_context(new_context)

        self.storage.save(new_blueprint)


@dataclass(frozen=True)
class DeleteComponentCommand:
    context: str
    name: str # Component name
    type: str # Component type (e.g. "aggregate", "context")


@dataclass
class DeleteComponent:
    storage: BlueprintStorage

    def execute(self, cmd: DeleteComponentCommand):
        blueprint = self.storage.load()
        if not blueprint:
            raise ValueError("Blueprint not found")

        if cmd.type.lower() == "context":
            new_blueprint = blueprint.delete_context(cmd.name)
        else:
            context = blueprint.get_context(cmd.context)
            if not context:
                raise ValueError(f"Context '{cmd.context}' not found")

            # Simplified logic: BoundedContext handles dispatch
            new_context = context.delete_component(cmd.name, cmd.type)
            new_blueprint = blueprint.update_context(new_context)

        self.storage.save(new_blueprint)
