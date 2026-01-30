from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.models import ValueObject


class ImplementationSpec(ValueObject):
    """Specification of an implementation to be generated."""

    name: PascalString = Field(default_factory=str)
    implements: PascalString
    technology: SnakeString
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    private_methods: list[MethodSpec] = Field(default_factory=list)

    def add_private_method(self, method: MethodSpec) -> "ImplementationSpec":
        if any(m.name == method.name for m in self.private_methods):
            raise ValueError(f"Method '{method.name}' already exists in implementation '{self.name}'.")
        return self.model_copy(update={"private_methods": self.private_methods + [method]})

    def update_private_method(self, method: MethodSpec) -> "ImplementationSpec":
        if not any(m.name == method.name for m in self.private_methods):
            raise ValueError(f"Method '{method.name}' not found in implementation '{self.name}'.")
        new_methods = [method if m.name == method.name else m for m in self.private_methods]
        return self.model_copy(update={"private_methods": new_methods})

    def delete_private_method(self, name: str) -> "ImplementationSpec":
        new_methods = [m for m in self.private_methods if str(m.name) != name]
        if len(new_methods) == len(self.private_methods):
            raise ValueError(f"Method '{name}' not found in implementation '{self.name}'.")
        return self.model_copy(update={"private_methods": new_methods})

    @classmethod
    def create(
        cls,
        name: str,
        implements: str,
        technology: str,
        description: str = "",
        attributes: list[AttributeSpec] | None = None,
        private_methods: list[MethodSpec] | None = None,
    ):
        return cls(
            name=PascalString(name),
            implements=PascalString(implements),
            technology=SnakeString(technology),
            description=description,
            attributes=attributes or [],
            private_methods=private_methods or [],
        )
