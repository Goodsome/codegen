from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.domain_definition.domain.value_objects.meta_enum_member import (
    EnumMemberSpec,
)


class EnumSpec(ValueObject):
    """Specification of an enum to be generated."""

    name: str
    description: str = Field(default_factory=str)
    members: list[EnumMemberSpec]
