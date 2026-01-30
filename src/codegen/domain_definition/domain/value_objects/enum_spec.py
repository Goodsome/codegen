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

    def add_member(self, member: EnumMemberSpec) -> "EnumSpec":
        if any(m.name == member.name for m in self.members):
            raise ValueError(f"Member '{member.name}' already exists in enum '{self.name}'.")
        return self.model_copy(update={"members": self.members + [member]})

    def update_member(self, member: EnumMemberSpec) -> "EnumSpec":
        if not any(m.name == member.name for m in self.members):
            raise ValueError(f"Member '{member.name}' not found in enum '{self.name}'.")
        new_members = [member if m.name == member.name else m for m in self.members]
        return self.model_copy(update={"members": new_members})

    def delete_member(self, name: str) -> "EnumSpec":
        new_members = [m for m in self.members if str(m.name) != name]
        if len(new_members) == len(self.members):
            raise ValueError(f"Member '{name}' not found in enum '{self.name}'.")
        return self.model_copy(update={"members": new_members})
