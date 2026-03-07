from codegen.domain_definition.domain.value_objects.type_definition import TypeDefinition
from codegen.shared.domain.value_objects.snake_string import SnakeString
from pydantic import Field


class AttributeSpec(TypeDefinition):
    """Standard specification for a class attribute."""

    name: SnakeString
    description: str = Field(default_factory=str)
    # type, container, optional, custom_type_string 继承自 TypeDefinition
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
            custom_type_string=None,
        )
