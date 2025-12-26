from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import Attribute


class MetaUseCaseCommand(ValueObject):
    """Specification of a use case command to be generated."""

    name: str
    attributes: list[Attribute] = Field(default_factory=list)
