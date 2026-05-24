from dataclasses import dataclass


@dataclass
class Arg:
    """Represents a single function/lambda parameter."""

    arg: str
    annotation: str | None = None
    type_comment: str | None = None
