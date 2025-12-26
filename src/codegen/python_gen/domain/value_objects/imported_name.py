from codegen.shared.models import ValueObject


class ImportedName(ValueObject):
    """Represents a name imported from another module."""

    name: str
    alias: str | None = None

    def render(self) -> str:
        if self.alias:
            return f"{self.name} as {self.alias}"
        return self.name
