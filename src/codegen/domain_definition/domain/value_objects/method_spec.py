from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.shared.domain.value_objects.naming_string import SnakeString
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.models import ValueObject


class MethodSpec(ValueObject):
    """Standard specification for a class method."""

    name: SnakeString
    description: str = Field(default_factory=str)
    inputs: list[AttributeSpec]
    output: MethodOutput
