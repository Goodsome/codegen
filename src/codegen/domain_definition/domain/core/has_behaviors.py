from typing import Self

from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from pydantic import BaseModel, Field


class HasBehaviors(BaseModel):
    """能力：拥有行为（方法）"""

    behaviors: list[MethodSpec] = Field(default_factory=list)

    def add_behavior(self: Self, behavior: MethodSpec) -> Self:
        """Add a MethodSpec behavior. Raises ValueError if behavior with same name exists."""
        for beh in self.behaviors:
            if beh.name == behavior.name:
                raise ValueError(
                    f"Behavior '{behavior.name}' already exists in '{self}'"
                )
        self.behaviors.append(behavior)
        return self

    def update_behavior(self: Self, behavior: MethodSpec) -> Self:
        """Update an existing MethodSpec behavior by name. Raises ValueError if not found."""
        for i, beh in enumerate(self.behaviors):
            if beh.name == behavior.name:
                self.behaviors[i] = behavior
                return self
        raise ValueError(
            f"Behavior '{behavior.name}' not found in '{self}'"
        )

    def remove_behavior(self: Self, name: SnakeString) -> Self:
        """Remove a MethodSpec behavior by name. Returns self for chaining."""
        self.behaviors = [beh for beh in self.behaviors if beh.name != name]
        return self

    def get_behavior(self: Self, name: SnakeString) -> MethodSpec:
        """Get a MethodSpec behavior by name. Raises ValueError if not found."""
        for beh in self.behaviors:
            if beh.name == name:
                return beh
        raise ValueError(f"Behavior '{name}' not found in '{self}'")
