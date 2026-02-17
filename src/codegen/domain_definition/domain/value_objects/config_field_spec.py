from codegen.shared.domain.value_objects.snake_string import SnakeString
from pydantic import Field
from codegen.shared.models import ValueObject


class ConfigFieldSpec(ValueObject):
    """Specification for a single configuration field."""

    name: SnakeString
    type: str
    default: str | None = Field(default=None)
    description: str = Field(default="")
    env_var: str | None = Field(default=None)
