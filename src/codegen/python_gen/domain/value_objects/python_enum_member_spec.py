from codegen.shared.domain.value_objects.macro_string import MacroString

from codegen.shared.domain.core import ValueObject
from pydantic import Field


class PythonEnumMemberSpec(ValueObject):
    """Represents an enum member in a Python module."""

    name: MacroString
    value: str | int | None = Field(default=None)
    description: str = Field(default_factory=str)

    @classmethod
    def create(
        cls, name: str, value: str | int | None = None, description: str = ""
    ) -> "PythonEnumMemberSpec":
        return cls(
            name=MacroString(name),
            value=value,
            description=description,
        )
