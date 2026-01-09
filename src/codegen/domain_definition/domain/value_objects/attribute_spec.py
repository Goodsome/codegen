from pydantic import Field
from codegen.shared.models import ValueObject


class AttributeSpec(ValueObject):
    """Standard specification for a class attribute."""

    name: str
    type: str
    description: str = Field(default_factory=str)
    optional: bool = Field(default_factory=bool)
