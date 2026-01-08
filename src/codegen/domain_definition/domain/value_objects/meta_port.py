from pydantic import Field
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.shared.models import ValueObject


class PortSpec(ValueObject):
    """Specification of a domain port to be generated."""

    name: str
    description: str = Field(default_factory=str)
    kind: str
    operations: list[MethodSpec] = Field(default_factory=list)
