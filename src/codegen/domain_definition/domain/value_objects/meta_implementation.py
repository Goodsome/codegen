from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.shared.models import ValueObject


class MetaImplementation(ValueObject):
    """Specification of an implementation to be generated."""

    name: str
    implements: str
    description: str = Field(default_factory=str)
    attributes: list[Attribute] = Field(default_factory=list)
