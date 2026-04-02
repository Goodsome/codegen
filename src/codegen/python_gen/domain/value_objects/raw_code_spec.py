from codegen.shared.domain.core import ValueObject


class RawCodeSpec(ValueObject):
    """Represents a block of raw source code."""

    code: str

    @classmethod
    def create(cls, code: str) -> "RawCodeSpec":
        return cls(code=code)
