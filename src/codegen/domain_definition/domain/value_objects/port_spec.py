from pydantic import Field, model_validator

from codegen.domain_definition.domain.enums import PortType
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject


class PortSpec(ValueObject):
    """Specification of a domain port to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    kind: PortType
    aggregate: PascalString | None = None
    operations: list[MethodSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        kind: PortType | str,
        description: str = "",
        aggregate: str | None = None,
        operations: list[MethodSpec] | None = None,
    ) -> "PortSpec":
        if isinstance(kind, str):
            kind = PortType(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            description=description,
            aggregate=aggregate and PascalString(aggregate),
            operations=operations or [],
        )

    def get_final_operations(self) -> list[MethodSpec]:
        default_operations: list[MethodSpec] = self.operations
        if self.kind is not PortType.REPOSITORY:
            return default_operations
        if self.aggregate is None:
            return default_operations
        save_method_spec = self.get_save_method_spec()
        if save_method_spec is not None:
            default_operations.append(save_method_spec)
        delete_method_spec = self.get_delete_method_spec()
        if delete_method_spec is not None:
            default_operations.append(delete_method_spec)
        find_by_id_method_spec = self.get_find_by_id_method_spec()
        if find_by_id_method_spec is not None:
            default_operations.append(find_by_id_method_spec)

        return default_operations

    def get_save_method_spec(self) -> MethodSpec | None:
        for operation in self.operations:
            if operation.name == "save":
                return None
        return MethodSpec.create(
            name="save",
            inputs=[AttributeSpec.create(name=self.aggregate, type=self.aggregate)],
            output=MethodOutput(type="None"),
        )

    def get_delete_method_spec(self) -> MethodSpec | None:
        for operation in self.operations:
            if operation.name == "delete":
                return None
        return MethodSpec.create(
            name="delete",
            inputs=[AttributeSpec.create(name=f"{self.aggregate}_id", type="UUID")],
            output=MethodOutput(type="None"),
        )

    def get_find_by_id_method_spec(self) -> MethodSpec | None:
        for operation in self.operations:
            if operation.name == "find_by_id":
                return None
        return MethodSpec.create(
            name="find_by_id",
            inputs=[AttributeSpec.create(name=f"{self.aggregate}_id", type="UUID")],
            output=MethodOutput(type=f"{self.aggregate} | None"),
        )
