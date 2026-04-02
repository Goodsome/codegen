from typing import Self, Iterable, ClassVar

from pydantic import Field, BaseModel

from codegen.domain_definition.domain.core.named_element_ops_mixin import NamedElementOpsMixin
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


class HasBehaviors(BaseModel, NamedElementOpsMixin):
    """能力：拥有行为（方法）"""

    behaviors: list[MethodSpec] = Field(default_factory=list)

    __pkg_name__: ClassVar[str]

    @property
    def root_pkg_name(self) -> str:
        raise NotImplementedError("Subclasses must implement 'test_package_name'")

    @property
    def entity_name(self) -> str:
        """Dynamic: test package name (e.g., entity name)"""
        raise NotImplementedError("Subclasses must implement 'test_package_name'")

    def add_behavior(self: Self, behavior: MethodSpec) -> Self:
        return self._add_item("behaviors", behavior, "Behavior")

    def update_behavior(self: Self, behavior: MethodSpec) -> Self:
        return self._update_item("behaviors", behavior, "Behavior")

    def remove_behavior(self: Self, name) -> Self:
        return self._remove_item("behaviors", name)

    def get_behavior(self: Self, name) -> MethodSpec:
        return self._get_item("behaviors", name, "Behavior")

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create test package for entity with behaviors that have rules."""
        modules = []
        for behavior in self.behaviors:
            tm = behavior.to_test_module_spec()
            bm = behavior.to_bindings_module_spec()
            if tm.functions:
                modules.append(tm)
                modules.append(bm)
        p = PackageSpec.create(name=self.entity_name, modules=modules)
        return PackageSpec.create(
            name=self.__pkg_name__,
            sub_packages=[p],
        )

    def to_function_specs(self: Self) -> list[FunctionSpec]:
        """Convert behaviors to a list of FunctionSpecs."""
        return [beh.to_function_spec(class_name=self.entity_name) for beh in self.behaviors]

    @classmethod
    def from_function_specs(cls: type[Self], methods: Iterable[FunctionSpec]) -> list[MethodSpec]:
        """将 FunctionSpec 列表逆向解析为 MethodSpec 列表"""
        return [
            MethodSpec.from_function_spec(method)
            for method in methods
        ]