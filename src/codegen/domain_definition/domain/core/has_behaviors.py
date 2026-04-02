from typing import Self, ClassVar

from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from pydantic import BaseModel, Field


class HasBehaviors(BaseModel):
    """能力：拥有行为（方法）"""

    behaviors: list[MethodSpec] = Field(default_factory=list)

    __root_pkg_name__: ClassVar[str]

    @property
    def test_package_name(self) -> str:
        """Dynamic: test package name (e.g., entity name)"""
        raise NotImplementedError("Subclasses must implement 'test_package_name'")

    def add_behavior(self: Self, behavior: MethodSpec) -> Self:
        """Add a MethodSpec behavior. Raises ValueError if behavior with same name exists."""
        for beh in self.behaviors:
            if beh.name == behavior.name:
                raise ValueError(
                    f"Behavior '{behavior.name}' already exists in '{self}'"
                )
        self.behaviors.append(behavior)
        return self

    def update_behavior(self: Self, behavior: MethodSpec) -> Self:
        """Update an existing MethodSpec behavior by name. Raises ValueError if not found."""
        for i, beh in enumerate(self.behaviors):
            if beh.name == behavior.name:
                self.behaviors[i] = behavior
                return self
        raise ValueError(
            f"Behavior '{behavior.name}' not found in '{self}'"
        )

    def remove_behavior(self: Self, name: SnakeString) -> Self:
        """Remove a MethodSpec behavior by name. Returns self for chaining."""
        self.behaviors = [beh for beh in self.behaviors if beh.name != name]
        return self

    def get_behavior(self: Self, name: SnakeString) -> MethodSpec:
        """Get a MethodSpec behavior by name. Raises ValueError if not found."""
        for beh in self.behaviors:
            if beh.name == name:
                return beh
        raise ValueError(f"Behavior '{name}' not found in '{self}'")

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create test package for entity with behaviors that have rules."""
        modules = []
        for behavior in self.behaviors:
            tm = behavior.to_test_module_spec()
            bm = behavior.to_bindings_module_spec()
            if tm.functions:
                modules.append(tm)
                modules.append(bm)
        p = PackageSpec.create(name=self.test_package_name, modules=modules)
        return PackageSpec.create(
            name=self.__test_root_pkg_name__,
            sub_packages=[p],
        )
