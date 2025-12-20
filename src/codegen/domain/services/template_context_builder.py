import re
from typing import List, Dict, Any, Optional, Set

from codegen.domain.aggregates.blueprint import Blueprint
from codegen.domain.services.naming_service import NamingService
from codegen.domain.value_objects.bounded_context import BoundedContext


class TemplateContextBuilder:
    """
    Transform domain blueprint into template contexts.
    """

    def __init__(self):
        self.naming = NamingService()
        self.registry = {}

    def build_registry(self, blueprint: Blueprint):
        """Builds a mapping of type names to their import paths."""
        self.registry = {}
        contexts: list[BoundedContext] = blueprint.contexts
        for ctx in contexts:
            for agg in ctx.aggregates:
                self.registry[agg.name] = (
                    f"from codegen.domain.aggregates.{self.naming.to_snake(agg.name)} import {agg.name}"
                )
            for vo in ctx.value_objects:
                self.registry[vo.name] = (
                    f"from codegen.domain.value_objects.{self.naming.to_snake(vo.name)} import {vo.name}"
                )
            for port in ctx.ports:
                self.registry[port.name] = (
                    f"from codegen.domain.ports.{self.naming.to_snake(port.name)} import {port.name}"
                )
            for svc in ctx.services:
                self.registry[svc.name] = (
                    f"from codegen.domain.services.{self.naming.to_snake(svc.name)} import {svc.name}"
                )

    def extract_types(self, type_strs: List[str]) -> Set[str]:
        types = set()
        for ts in type_strs:
            if not ts:
                continue
            found = re.findall(r"\b\w+\b", ts)
            types.update(found)
        return types

    def resolve_imports(
        self, types_used: Set[str], current_name: str, force_dataclass: bool = False
    ) -> List[str]:
        imports = []
        typing_keywords = {"List", "Dict", "Optional", "Any", "Union"}
        used_typing = types_used.intersection(typing_keywords)

        if used_typing:
            imports.append(f"from typing import {', '.join(sorted(used_typing))}")

        if force_dataclass:
            imports.append("from dataclasses import dataclass")

        for t in types_used:
            if t != current_name and t in self.registry:
                imports.append(self.registry[t])

        return sorted(list(set(imports)))

    def build_context(self, target: Any) -> Dict[str, Any]:
        """
        Builds a context dictionary for a template based on the target domain object.
        """
        # Generic context building logic
        # For a real robust implementation, we might want specialized methods for each type
        if hasattr(target, "model_dump"):
            ctx = target.model_dump()
        else:
            ctx = vars(target).copy()

        # Add common helpers
        ctx["target_name"] = getattr(target, "name", "unknown")

        # Add imports if it's a component that needs them
        types_used = set()
        force_dataclass = False

        if hasattr(target, "attributes"):
            types_used.update(
                self.extract_types(
                    [a.name if hasattr(a, "type") else "" for a in target.attributes]
                )
            )
            # Wait, attributes in domain model are objects.
            # a.type should be the type string.
            types_used.update(
                self.extract_types([getattr(a, "type", "") for a in target.attributes])
            )

        if hasattr(target, "operations"):
            for op in target.operations:
                types_used.update(
                    self.extract_types([getattr(i, "type", "") for i in op.inputs])
                )
                types_used.update(self.extract_types([getattr(op, "output_type", "")]))

        # Use cases have specific needs
        if hasattr(target, "command") and hasattr(target, "result"):
            force_dataclass = True
            types_used.update(
                self.extract_types(
                    [getattr(a, "type", "") for a in target.command.attributes]
                )
            )
            types_used.update(
                self.extract_types(
                    [getattr(a, "type", "") for a in target.result.attributes]
                )
            )
            if getattr(target, "depends_on_services", []) or getattr(
                target, "depends_on_ports", []
            ):
                types_used.add("Any")
                # Also add the specific ports/services to imports if they are in registry
                types_used.update(getattr(target, "depends_on_services", []))
                types_used.update(getattr(target, "depends_on_ports", []))

        ctx["imports"] = self.resolve_imports(
            types_used, ctx.get("name", ""), force_dataclass
        )

        return ctx
