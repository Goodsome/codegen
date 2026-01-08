from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import AttributeSpec
from codegen.shared.models import ValueObject


class UseCaseResultSpec(ValueObject):
    """Specification of a use case result to be generated."""

    name: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
