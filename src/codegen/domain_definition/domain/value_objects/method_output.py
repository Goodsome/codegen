from codegen.shared.models import ValueObject


class MethodOutput(ValueObject):
    """Specification of the output of a method."""

    type: str
