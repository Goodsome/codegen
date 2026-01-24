from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.domain_definition.domain.value_objects.enum_member_spec import (
    EnumMemberSpec,
)


class EnumSpec(ValueObject):
    """Specification of an enum to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    members: list[EnumMemberSpec]
