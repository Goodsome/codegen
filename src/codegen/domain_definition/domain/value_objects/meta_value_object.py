from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec


class MetaValueObject(ValueObject):
    """Specification of a value object to be generated."""

    name: str
    description: str = Field(default_factory=str)
    attributes: list[Attribute] = Field(default_factory=list)
    behaviors: list[MethodSpec] = Field(default_factory=list)
