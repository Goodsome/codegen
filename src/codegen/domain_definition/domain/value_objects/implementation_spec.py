from codegen.shared.domain.value_objects.naming_string import SnakeString
from codegen.shared.domain.value_objects.naming_string import PascalString
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.models import ValueObject


class ImplementationSpec(ValueObject):
    """Specification of an implementation to be generated."""

    implements: PascalString
    technology: SnakeString
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
            implements=PascalString(implements),
            technology=SnakeString(technology),
            description=description,
            attributes=attributes or [],
            private_methods=private_methods or [],
        )
