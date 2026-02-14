from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.bootstrap_spec import BootstrapSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.test_config import TestConfig
from typing import Any, Union


class Blueprint(ValueObject):
    """Root of the generation model. Represents the entire project definition."""

    name: PascalString
    description: str
    layout: str = Field(default_factory=str)
    contexts: list[BoundedContext] = Field(default_factory=list)
    bootstrap: BootstrapSpec = Field(default_factory=BootstrapSpec)
    test_config: TestConfig | None = None

    @classmethod
    def create(
        cls: Any,
        name: Union[str, PascalString],
        description: str,
        layout: str = "",
        contexts: list[BoundedContext] | None = None,
        bootstrap: BootstrapSpec | None = None,
        test_config: TestConfig | None = None,
    ) -> Any:

        if contexts is None:
            contexts = []
        if bootstrap is None:
            bootstrap = BootstrapSpec()
        if isinstance(name, str):
            name = PascalString(name)
        return cls(
            name=name,
            description=description,
            layout=layout,
            contexts=contexts,
            bootstrap=bootstrap,
            test_config=test_config,
        )

    def add_context(self, context: BoundedContext) -> "Blueprint":
        if any(c.name == context.name for c in self.contexts):
            raise ValueError(f"Context '{context.name}' already exists.")
        return self.model_copy(update={"contexts": self.contexts + [context]})

    def update_context(self, context: BoundedContext) -> "Blueprint":
        if not any(c.name == context.name for c in self.contexts):
            raise ValueError(f"Context '{context.name}' not found.")
        new_list = [context if c.name == context.name else c for c in self.contexts]
        return self.model_copy(update={"contexts": new_list})

    def delete_context(self, name: str) -> "Blueprint":
        target_name = PascalString(name)
        new_list = [c for c in self.contexts if c.name != target_name]
        if len(new_list) == len(self.contexts):
            raise ValueError(f"Context '{name}' not found.")
        return self.model_copy(update={"contexts": new_list})

    def get_context(self, name: str) -> BoundedContext | None:
        target_name = PascalString(name)
        return next((c for c in self.contexts if c.name == target_name), None)
