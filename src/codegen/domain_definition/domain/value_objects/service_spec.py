from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec


class ServiceSpec(ValueObject):
    """Specification of a domain service to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    dependencies: list[AttributeSpec] = Field(default_factory=list)
    operations: list[MethodSpec] = Field(default_factory=list)

    def add_operation(self, operation: MethodSpec) -> "ServiceSpec":
        if any(op.name == operation.name for op in self.operations):
            raise ValueError(f"Operation '{operation.name}' already exists in service '{self.name}'.")
        return self.model_copy(update={"operations": self.operations + [operation]})

    def update_operation(self, operation: MethodSpec) -> "ServiceSpec":
        if not any(op.name == operation.name for op in self.operations):
            raise ValueError(f"Operation '{operation.name}' not found in service '{self.name}'.")
        new_ops = [operation if op.name == operation.name else op for op in self.operations]
        return self.model_copy(update={"operations": new_ops})

    def delete_operation(self, name: str) -> "ServiceSpec":
        new_ops = [op for op in self.operations if str(op.name) != name]
        if len(new_ops) == len(self.operations):
            raise ValueError(f"Operation '{name}' not found in service '{self.name}'.")
        return self.model_copy(update={"operations": new_ops})
