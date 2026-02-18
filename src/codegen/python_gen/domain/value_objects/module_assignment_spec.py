
from codegen.shared.models import ValueObject
from typing import Optional

class ModuleAssignmentSpec(ValueObject):
    """Represents a top-level assignment in a module."""
    
    name: str
    value: str
    type_annotation: Optional[str] = None
    
    @classmethod
    def create(cls, name: str, value: str, type_annotation: str | None = None) -> "ModuleAssignmentSpec":
        return cls(name=name, value=value, type_annotation=type_annotation)
