from codegen.domain_definition.domain.enums import PortType
from pydantic import Field
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.shared.models import ValueObject


class PortSpec(ValueObject):
    """Specification of a domain port to be generated."""

    name: str
    description: str = Field(default_factory=str)
    kind: PortType
    operations: list[MethodSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        kind: PortType | str,
        description: str = "",
        operations: list[MethodSpec] | None = None,
    ) -> "PortSpec":
        if isinstance(kind, str):
            kind = PortType(kind)
        return cls(
            name=name,
            kind=kind,
            description=description,
            operations=operations or [],
        )
