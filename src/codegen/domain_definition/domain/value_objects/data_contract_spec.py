from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.shared.models import ValueObject
from pydantic import Field


class DataContractSpec(ValueObject):
    """Generic data contract specification for use case command/query/result."""

    name: str
    description: str
    attributes: list[AttributeSpec] = Field(default_factory=list)

    def to_class_spec(self) -> ClassSpec:
        """Convert DataContractSpec to ClassSpec with BaseModel inheritance."""
        variable_specs = [
            attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
            for attr in self.attributes
        ]
        return ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=["BaseModel"],
            attributes=variable_specs,
        )

    @classmethod
    def from_class_spec(cls, class_spec: ClassSpec) -> "DataContractSpec":
        """Convert ClassSpec back to DataContractSpec."""
        attributes = [
            AttributeSpec.from_variable_spec(attr) for attr in class_spec.attributes
        ]
        return cls(
            name=str(class_spec.name),
            description=class_spec.description,
            attributes=attributes,
        )
