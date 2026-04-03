from typing import Iterator, Self, Iterable
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from pydantic import RootModel, Field


class MethodSpecList(RootModel[list[MethodSpec]]):
    root: list[MethodSpec] = Field(default_factory=list)
    
    def __iter__(self) -> Iterator[MethodSpec]: # type: ignore
        return iter(self.root)
        
    def add(self, method_spec: MethodSpec) -> Self:
        for existing in self.root:
            if existing.name == method_spec.name:
                raise ValueError(f"MethodSpec with name {method_spec.name} already exists")
        self.root.append(method_spec)
        return self
    
    def get(self, name: SnakeString) -> MethodSpec:
        for existing in self.root:
            if existing.name == name:
                return existing
        raise ValueError(f"MethodSpec with name {name} not found")
    
    def update(self, method_spec: MethodSpec) -> Self:
        for i, existing in enumerate(self.root):
            if existing.name == method_spec.name:
                self.root[i] = method_spec
                return self
        raise ValueError(f"MethodSpec with name {method_spec.name} not found")
    
    def remove(self, name: SnakeString) -> Self:
        for i, existing in enumerate(self.root):
            if existing.name == name:
                self.root.pop(i)
                return self
        raise ValueError(f"MethodSpec with name {name} not found")
    
    def to_function_specs(self: Self) -> list[FunctionSpec]:
        """Convert behaviors to a list of FunctionSpecs."""
        return [beh.to_function_spec() for beh in self.root]

    @classmethod
    def from_function_specs(cls: type[Self], methods: Iterable[FunctionSpec]) -> Self:
        """将 FunctionSpec 列表逆向解析为 MethodSpec 列表"""
        return cls(root=[
            MethodSpec.from_function_spec(method)
            for method in methods
        ])
        
    def to_test_modules(self: Self) -> list[ModuleSpec]:
        """Create test package for entity with behaviors that have rules."""
        modules = []
        for ms in self.root:
            tm = ms.to_test_module_spec()
            bm = ms.to_bindings_module_spec()
            if tm.functions:
                modules.append(tm)
                modules.append(bm)
        return modules