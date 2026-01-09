from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.enums import PortType


class ImplementationSpec(ValueObject):
    """Specification of an implementation to be generated."""

    implements: str
    technology: str
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    private_methods: list[MethodSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        implements: str,
        technology: str,
        description: str = "",
        attributes: list[AttributeSpec] | None = None,
        private_methods: list[MethodSpec] | None = None,
    ):
        return cls(
            implements=implements,
            technology=technology,
            description=description,
            attributes=attributes or [],
            private_methods=private_methods or [],
        )
