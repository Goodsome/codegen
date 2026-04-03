from typing import Iterator, Self, Iterable

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from pydantic import RootModel, Field


class AttributeSpecList(RootModel[list[AttributeSpec]]):
    root: list[AttributeSpec] = Field(default_factory=list)

    def __iter__(self) -> Iterator[AttributeSpec]:  # type: ignore
        return iter(self.root)

    def add(self, attribute_spec: AttributeSpec) -> Self:
        for existing in self.root:
            if existing.name == attribute_spec.name:
                raise ValueError(
                    f"AttributeSpec with name {attribute_spec.name} already exists"
                )
        self.root.append(attribute_spec)
        return self

    def get(self, name: SnakeString) -> AttributeSpec:
        for existing in self.root:
            if existing.name == name:
                return existing
        raise ValueError(f"AttributeSpec with name {name} not found")

    def update(self, attribute_spec: AttributeSpec) -> Self:
        for i, existing in enumerate(self.root):
            if existing.name == attribute_spec.name:
                self.root[i] = attribute_spec
                return self
        raise ValueError(f"AttributeSpec with name {attribute_spec.name} not found")

    def remove(self, name: SnakeString) -> Self:
        for i, existing in enumerate(self.root):
            if existing.name == name:
                self.root.pop(i)
                return self
        raise ValueError(f"AttributeSpec with name {name} not found")

    def to_variable_specs(
        self: Self, flavor: FieldFlavor | None = None
    ) -> list[VariableSpec]:
        """Convert attributes to a list of VariableSpecs."""
        return [attr.to_variable_spec(flavor=flavor) for attr in self.root]

    @classmethod
    def from_variable_specs(cls: type[Self], specs: Iterable[VariableSpec]) -> Self:
        """Convert VariableSpec list to AttributeSpecList."""
        return cls(root=[AttributeSpec.from_variable_spec(spec) for spec in specs])
