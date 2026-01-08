from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import AttributeSpec


class UseCaseCommandSpec(ValueObject):
    """Specification of a use case command to be generated."""

    name: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
