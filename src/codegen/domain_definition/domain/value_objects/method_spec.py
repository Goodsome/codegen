from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute import Attribute
from codegen.shared.models import ValueObject


class MethodSpec(ValueObject):
    """Standard specification for a class method."""

    name: str
    description: str = Field(default_factory=str)
    inputs: list[Attribute]
    output: MethodOutput
