from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)


class InfrastructureSpec(ValueObject):
    """Specification of an infrastructure to be generated."""

    implementations: list[ImplementationSpec] = Field(default_factory=list)

    def add_implementation(self, implementation: ImplementationSpec) -> "InfrastructureSpec":
        if any(i.name == implementation.name for i in self.implementations):
            raise ValueError(f"Implementation '{implementation.name}' already exists.")
        return self.model_copy(
            update={"implementations": self.implementations + [implementation]}
        )

    def update_implementation(self, implementation: ImplementationSpec) -> "InfrastructureSpec":
        if not any(i.name == implementation.name for i in self.implementations):
            raise ValueError(f"Implementation '{implementation.name}' not found.")
        new_list = [
            implementation if i.name == implementation.name else i
            for i in self.implementations
        ]
        return self.model_copy(update={"implementations": new_list})

    def delete_implementation(self, name: str) -> "InfrastructureSpec":
        new_list = [i for i in self.implementations if str(i.name) != name]
        if len(new_list) == len(self.implementations):
            raise ValueError(f"Implementation '{name}' not found.")
        return self.model_copy(update={"implementations": new_list})
