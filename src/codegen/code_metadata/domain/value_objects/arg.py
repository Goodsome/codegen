from codegen.shared.domain.core import ValueObject


class Arg(ValueObject):
    """Represents a single function/lambda parameter."""

    arg: str
    annotation: str | None = None
    type_comment: str | None = None
