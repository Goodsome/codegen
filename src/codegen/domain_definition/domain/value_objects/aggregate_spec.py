from codegen.shared.domain.value_objects.naming_string import PascalString
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec


class AggregateSpec(ValueObject):
    """Specification of a domain aggregate to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    behaviors: list[MethodSpec] = Field(default_factory=list)
