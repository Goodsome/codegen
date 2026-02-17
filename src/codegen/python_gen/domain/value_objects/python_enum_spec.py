

from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.python_gen.domain.value_objects.python_enum_member_spec import (
    PythonEnumMemberSpec,
)


class PythonEnumSpec(ValueObject):
    """Represents an enum in a Python module."""

    name: PascalString
    description: str = Field(default_factory=str)
    decorators: list[str] = Field(default_factory=list)
    base_class: str = Field(default_factory=str)
    members: list[PythonEnumMemberSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        decorators: list[str] | None = None,
        base_class: str = "Enum",
        members: list[PythonEnumMemberSpec] | None = None,
    ) -> "PythonEnumSpec":
        return cls(
            name=PascalString(name),
            description=description,
            decorators=decorators or [],
            base_class=base_class,
            members=members or [],
        )


