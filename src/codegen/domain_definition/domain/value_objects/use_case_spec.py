from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.shared.domain.value_objects.pascal_string import PascalString
from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.data_contract_spec import (
    DataContractSpec,
)


class UseCaseSpec(ValueObject):
    """Specification of a use case to be generated."""

    name: PascalString
    kind: UseCaseKind
    dependencies: list[AttributeSpec] = Field(default_factory=list)
    description: str = Field(default_factory=str)
    command: DataContractSpec = Field(default_factory=DataContractSpec)
    query: DataContractSpec = Field(default_factory=DataContractSpec)
    result: DataContractSpec = Field(default_factory=DataContractSpec)

    @classmethod
    def create(
        cls,
        name: str,
        kind: str | UseCaseKind,
        dependencies: list[AttributeSpec] | None = None,
        description: str = "",
        command: DataContractSpec | None = None,
        query: DataContractSpec | None = None,
        result: DataContractSpec | None = None,
    ):
        if dependencies is None:
            dependencies = []
        if command is None:
            command = DataContractSpec()
        if query is None:
            query = DataContractSpec()
        if result is None:
            result = DataContractSpec()
        if isinstance(kind, str):
            kind = UseCaseKind(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            dependencies=dependencies,
            description=description,
            command=command,
            query=query,
            result=result,
        )
