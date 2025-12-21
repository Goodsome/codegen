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
                    f"from codegen.{ctx.name}.domain.aggregates.{self.naming.to_snake(agg.name)} import {agg.name}"
                )
            for vo in ctx.value_objects:
                self.registry[vo.name] = (
                    f"from codegen.{ctx.name}.domain.value_objects.{self.naming.to_snake(vo.name)} import {vo.name}"
                )
            for port in ctx.ports:
                self.registry[port.name] = (
                    f"from codegen.{ctx.name}.domain.ports.{self.naming.to_snake(port.name)} import {port.name}"
                )
            for svc in ctx.services:
                self.registry[svc.name] = (
                    f"from codegen.{ctx.name}.domain.services.{self.naming.to_snake(svc.name)} import {svc.name}"
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
        # Build a context without recursively converting nested domain objects into dicts.
        # Jinja templates rely on attribute access (e.g. attr.name), so we must preserve
        # nested objects like Attribute/MethodSpec instead of `model_dump()`.
        raw = vars(target).copy()
        ctx = {k: v for k, v in raw.items() if not k.startswith("_")}

        # Expose the original object for templates that want direct object access.
        ctx["target"] = target

        # Add common helpers
        ctx["target_name"] = getattr(target, "name", "unknown")

        # Add imports if it's a component that needs them
        types_used = set()
        force_dataclass = False

        if hasattr(target, "attributes"):
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

        ctx["imports"] = self.resolve_imports(
            types_used, ctx.get("name", ""), force_dataclass
        )

        return ctx
