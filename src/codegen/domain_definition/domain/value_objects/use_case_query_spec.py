from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.models import ValueObject
from pydantic import Field


class UseCaseQuerySpec(ValueObject):
    """Specification of a use case command to be generated."""

    name: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
