from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.meta_bootstrap import MetaBootstrap
from pydantic import Field


class Blueprint(ValueObject):
    """Root of the generation model. Represents the entire project definition."""

    name: str
    description: str
    layout: str
    contexts: list[BoundedContext] = Field(default_factory=list)
    bootstrap: MetaBootstrap = Field(default_factory=MetaBootstrap)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        layout: str = "",
        contexts: list[BoundedContext] | None = None,
        bootstrap: MetaBootstrap | None = None,
    ):
        if contexts is None:
            contexts = []
        if bootstrap is None:
            bootstrap = MetaBootstrap()
        return cls(
            name=name,
            description=description,
            layout=layout,
            contexts=contexts,
            bootstrap=bootstrap,
        )
