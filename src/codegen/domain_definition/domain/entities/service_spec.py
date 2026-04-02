from typing import Iterable, Self

from pydantic import Field

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.core import Entity


class ServiceSpec(Entity):
    """Specification of a domain service to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    dependencies: list[AttributeSpec] = Field(default_factory=list)
    operations: list[MethodSpec] = Field(default_factory=list)

    def to_module_spec(self) -> ModuleSpec:
        """将 ServiceSpec 转换为 ModuleSpec"""
        attributes = [
            attr.to_variable_spec(flavor=FieldFlavor.DATACLASS)
            for attr in self.dependencies
        ]
        methods = [
            method.to_function_spec(type=FunctionType.INSTANCE_METHOD)
            for method in self.operations
        ]
        class_spec = ClassSpec.create(
            name=self.name,
            description=self.description,
            decorators=["dataclass"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def to_package_spec(cls, services: Iterable[Self]) -> PackageSpec:
        """将多个 ServiceSpec 转换为一个 'services' 包"""
        modules = [service.to_module_spec() for service in services]
        return PackageSpec.create(name="services", modules=modules)

    @classmethod
    def from_module_spec(cls, module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 ServiceSpec"""
        cls_spec = module.classes[0]
        attributes = [
            AttributeSpec.from_variable_spec(attr) for attr in cls_spec.attributes
        ]
        operations = [
            MethodSpec.from_function_spec(method) for method in cls_spec.methods
        ]
        return cls(
            name=cls_spec.name,
            description=cls_spec.description,
            dependencies=attributes,
            operations=operations,
        )

    @classmethod
    def from_package_spec(cls, package: PackageSpec) -> list[Self]:
        """将 'services' 包逆向解析为 ServiceSpec 列表"""
        if package.name != "services":
            return []
        services: list[Self] = []
        for module in package.modules:
            if module.is_init_module():
                continue
            services.append(cls.from_module_spec(module))
        return services

    def update(self, description: str | None = None) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if description is not None:
            self.description = description

    def add_dependency(self, dependency: AttributeSpec) -> Self:
        """Add an AttributeSpec dependency. Raises ValueError if dependency with same name exists."""
        for dep in self.dependencies:
            if dep.name == dependency.name:
                raise ValueError(
                    f"Dependency '{dependency.name}' already exists in service '{self.name}'"
                )
        self.dependencies.append(dependency)
        return self

    def update_dependency(self, dependency: AttributeSpec) -> Self:
        """Update an existing AttributeSpec dependency by name. Raises ValueError if not found."""
        for i, dep in enumerate(self.dependencies):
            if dep.name == dependency.name:
                self.dependencies[i] = dependency
                return self
        raise ValueError(
            f"Dependency '{dependency.name}' not found in service '{self.name}'"
        )

    def remove_dependency(self, name: SnakeString) -> Self:
        """Remove an AttributeSpec dependency by name. Returns self for chaining."""
        self.dependencies = [dep for dep in self.dependencies if dep.name != name]
        return self

    def get_dependency(self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec dependency by name. Raises ValueError if not found."""
        for dep in self.dependencies:
            if dep.name == name:
                return dep
        raise ValueError(f"Dependency '{name}' not found in service '{self.name}'")

    def add_operation(self, operation: MethodSpec) -> Self:
        """Add a MethodSpec operation. Raises ValueError if operation with same name exists."""
        for op in self.operations:
            if op.name == operation.name:
                raise ValueError(
                    f"Operation '{operation.name}' already exists in service '{self.name}'"
                )
        self.operations.append(operation)
        return self

    def update_operation(self, operation: MethodSpec) -> Self:
        """Update an existing MethodSpec operation by name. Raises ValueError if not found."""
        for i, op in enumerate(self.operations):
            if op.name == operation.name:
                self.operations[i] = operation
                return self
        raise ValueError(
            f"Operation '{operation.name}' not found in service '{self.name}'"
        )

    def remove_operation(self, name: SnakeString) -> Self:
        """Remove a MethodSpec operation by name. Returns self for chaining."""
        self.operations = [op for op in self.operations if op.name != name]
        return self

    def get_operation(self, name: SnakeString) -> MethodSpec:
        """Get a MethodSpec operation by name. Raises ValueError if not found."""
        for op in self.operations:
            if op.name == name:
                return op
        raise ValueError(f"Operation '{name}' not found in service '{self.name}'")
