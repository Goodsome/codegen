from pydantic import Field

from codegen.shared.domain.core import ValueObject
from typing import Optional


class ModuleAssignmentSpec(ValueObject):
    """Represents a top-level assignment in a module."""

    name: str
    value: str
    type_annotation: Optional[str] = None
    require_types: list[str] = Field(default_factory=list)

    @classmethod
    def create(
        cls, name: str, value: str, type_annotation: str | None = None
    ) -> "ModuleAssignmentSpec":
        return cls(name=name, value=value, type_annotation=type_annotation)

    def get_required_types(self) -> set[str]:
        return set(self.require_types)
