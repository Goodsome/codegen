from codegen.shared.domain.value_objects.naming_string import SnakeString
from pydantic import Field
from codegen.shared.models import ValueObject


class AttributeSpec(ValueObject):
    """Standard specification for a class attribute."""

    name: SnakeString
    type: str
    description: str = Field(default_factory=str)
    optional: bool = Field(default_factory=bool)
