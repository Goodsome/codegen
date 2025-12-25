from codegen.domain.shared.models import ValueObject


class ImportedName(ValueObject):
    """Represents a name imported from another module."""

    name: str
    alias: str | None = None
