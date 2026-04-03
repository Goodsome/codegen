from typing import Iterator, Self, Iterable

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from pydantic import RootModel, Field


class DependencySpecList(RootModel[list[AttributeSpec]]):
    root: list[AttributeSpec] = Field(default_factory=list)

    def __iter__(self) -> Iterator[AttributeSpec]:  # type: ignore
        return iter(self.root)

    def add(self, dependency_spec: AttributeSpec) -> Self:
        for existing in self.root:
            if existing.name == dependency_spec.name:
                raise ValueError(
                    f"Dependency with name {dependency_spec.name} already exists"
                )
        self.root.append(dependency_spec)
        return self

    def get(self, name: SnakeString) -> AttributeSpec:
        for existing in self.root:
            if existing.name == name:
                return existing
        raise ValueError(f"Dependency with name {name} not found")

    def update(self, dependency_spec: AttributeSpec) -> Self:
        for i, existing in enumerate(self.root):
            if existing.name == dependency_spec.name:
                self.root[i] = dependency_spec
                return self
        raise ValueError(f"Dependency with name {dependency_spec.name} not found")

    def remove(self, name: SnakeString) -> Self:
        for i, existing in enumerate(self.root):
            if existing.name == name:
                self.root.pop(i)
                return self
        raise ValueError(f"Dependency with name {name} not found")

    def to_variable_specs(
        self: Self, flavor: FieldFlavor | None = None
    ) -> list[VariableSpec]:
        """Convert dependencies to a list of VariableSpecs."""
        return [dep.to_variable_spec(flavor=flavor) for dep in self.root]

    @classmethod
    def from_variable_specs(cls: type[Self], specs: Iterable[VariableSpec]) -> Self:
        """Convert VariableSpec list to DependencySpecList."""
        return cls(root=[AttributeSpec.from_variable_spec(spec) for spec in specs])
