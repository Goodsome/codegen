from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.models import ValueObject


class DataContractSpec(ValueObject):
    """Generic data contract specification for use case command/query/result."""

    name: str = Field(default_factory=str)
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
