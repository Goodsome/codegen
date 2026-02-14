from typing import Any, Union

from pydantic import Field

from codegen.domain_definition.domain.value_objects.bootstrap_spec import BootstrapSpec
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject


class Blueprint(ValueObject):
    """Root of the generation model. Represents the entire project definition."""

    name: PascalString
    description: str
    layout: str = Field(default_factory=str)
    contexts: list[BoundedContext] = Field(default_factory=list)
    bootstrap: BootstrapSpec = Field(default_factory=BootstrapSpec)

    @classmethod
    def create(
        cls: Any,
        name: Union[str, PascalString],
        description: str,
        layout: str = "",
        contexts: list[BoundedContext] | None = None,
        bootstrap: BootstrapSpec | None = None,
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
        )
