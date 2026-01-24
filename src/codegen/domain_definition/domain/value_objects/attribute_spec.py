from codegen.shared.domain.enums import ContainerType
from codegen.shared.domain.value_objects.snake_string import SnakeString
from pydantic import Field
from codegen.shared.models import ValueObject


class AttributeSpec(ValueObject):
    """Standard specification for a class attribute."""

    name: SnakeString
    description: str = Field(default_factory=str)
    type: str
    container: ContainerType = Field(default=ContainerType.NONE)
    optional: bool = Field(default_factory=bool)
    default: str | None = Field(default=None)

    @classmethod
    def create(
        cls,
        name: str,
        type: str,
        optional: bool = False,
    ):
        return cls(
            name=SnakeString(name),
            type=type,
            optional=optional,
        )
