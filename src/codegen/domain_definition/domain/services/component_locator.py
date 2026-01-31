from dataclasses import dataclass
from typing import Any

from codegen.domain_definition.domain.value_objects.bounded_context import BoundedContext


@dataclass
class ComponentLocator:
    """Responsible for finding any component within a BoundedContext."""

    # Type String -> Find Handler
    _FIND_HANDLERS = {
        # Domain layer
        "aggregate": lambda ctx, name: next((x for x in ctx.domain.aggregates if str(x.name) == name), None),
        "entity": lambda ctx, name: next((x for x in ctx.domain.entities if str(x.name) == name), None),
        "value_object": lambda ctx, name: next((x for x in ctx.domain.value_objects if str(x.name) == name), None),
        "valueobject": lambda ctx, name: next((x for x in ctx.domain.value_objects if str(x.name) == name), None),
        "service": lambda ctx, name: next((x for x in ctx.domain.services if str(x.name) == name), None),
        "enum": lambda ctx, name: next((x for x in ctx.domain.enums if str(x.name) == name), None),
        # Application layer
        "use_case": lambda ctx, name: next((x for x in ctx.application.use_cases if str(x.name) == name), None),
        "usecase": lambda ctx, name: next((x for x in ctx.application.use_cases if str(x.name) == name), None),
        # Infrastructure layer
        "implementation": lambda ctx, name: next((x for x in ctx.infrastructure.implementations if str(x.name) == name), None),
    }

    def _find_port_strategy(self, context: BoundedContext, name: str) -> Any:
        """Strategy to find port: Domain layer first, then Application layer."""
        p = next((x for x in context.domain.ports if str(x.name) == name), None)
        if not p:
            p = next((x for x in context.application.ports if str(x.name) == name), None)
        return p

    def find_parent_component(self, context: BoundedContext, name: str, type_hint: str) -> Any:
        """
        Finds a component by name and type hint.
        type_hint: 'aggregate', 'service', 'port', 'implementation', 'entity', 'value-object', 'use-case', 'enum'
        """
        type_clean = type_hint.lower().replace("-", "_")

        # Special handling for Port (dual-location)
        if type_clean == "port":
            return self._find_port_strategy(context, name)

        handler = self._FIND_HANDLERS.get(type_clean)
        if handler:
            return handler(context, name)

        return None
