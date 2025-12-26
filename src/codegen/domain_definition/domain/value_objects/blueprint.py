from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.meta_bootstrap import MetaBootstrap


class Blueprint(ValueObject):
    """Root of the generation model. Represents the entire project definition."""

    name: str
    description: str
    layout: str
    contexts: list[BoundedContext]
    bootstrap: MetaBootstrap
