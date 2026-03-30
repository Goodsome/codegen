from typing import Iterable, Self

from pydantic import Field

from codegen.domain_definition.domain.enums import PortType
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity


class PortSpec(Entity):
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
    ) -> Self:
        if isinstance(kind, str):
            kind = PortType(kind)
        if aggregate is not None:
            aggregate = PascalString(aggregate)
        return cls(
            name=PascalString(name),
            kind=kind,
            description=description,
            aggregate=aggregate,
            operations=operations or [],
        )

    def to_module_spec(self) -> ModuleSpec:
        """将 PortSpec 转换为 ModuleSpec"""
        methods = [
            method.to_function_spec(
                type=FunctionType.INSTANCE_METHOD,
                class_name=self.name,
            )
            for method in self.get_final_operations()
        ]
        for method in methods:
            if "abstractmethod" not in method.decorators:
                method.decorators.append("abstractmethod")
        class_spec = ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=["ABC"],
            methods=methods,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def to_package_spec(cls, ports: Iterable[Self]) -> PackageSpec:
        """将多个 PortSpec 转换为一个 'ports' 包"""
        modules = [port.to_module_spec() for port in ports]
        return PackageSpec.create(name="ports", modules=modules)

    @classmethod
    def from_module_spec(cls, module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 PortSpec"""
        cls_spec = module.classes[0]
        operations = [
            MethodSpec.from_function_spec(method) for method in cls_spec.methods
        ]
        if "Repository" in cls_spec.name:
            kind = "repository"
            aggregate = cls_spec.name.replace("Repository", "")
        else:
            kind = "adapter"
            aggregate = None
        return cls.create(
            name=cls_spec.name,
            kind=kind,
            description=cls_spec.description,
            aggregate=aggregate,
            operations=operations,
        )

    @classmethod
    def from_package_spec(cls, package: PackageSpec) -> list[Self]:
        """将 'ports' 包逆向解析为 PortSpec 列表"""
        if package.name != "ports":
            return []
        ports: list[Self] = []
        for module in package.modules:
            if module.is_init_module():
                continue
            ports.append(cls.from_module_spec(module))
        return ports

    def get_final_operations(self) -> list[MethodSpec]:
        default_operations: list[MethodSpec] = self.operations
        if self.kind is not PortType.REPOSITORY:
            return default_operations
        if self.aggregate is None:
            return default_operations

        return default_operations

    def update_metadata(
        self,
        kind: str,
        description: str,
        aggregate: str | None
    ) -> None:
        """Update scalar metadata fields (e.g., description). Preserves internal structure."""
        self.description = description
        self.kind = PortType(kind)
        if aggregate is not None:
            aggregate = PascalString(aggregate)
        self.aggregate = aggregate

    def add_operation(self, operation: MethodSpec) -> Self:
        """Add a MethodSpec operation. Raises ValueError if operation with same name exists."""
        for op in self.operations:
            if op.name == operation.name:
                raise ValueError(f"Operation '{operation.name}' already exists in port '{self.name}'")
        self.operations.append(operation)
        return self

    def update_operation(self, operation: MethodSpec) -> Self:
        """Update an existing MethodSpec operation by name. Raises ValueError if not found."""
        for i, op in enumerate(self.operations):
            if op.name == operation.name:
                self.operations[i] = operation
                return self
        raise ValueError(f"Operation '{operation.name}' not found in port '{self.name}'")

    def remove_operation(self, name: SnakeString) -> Self:
        """Remove a MethodSpec operation by name. Returns self for chaining."""
        self.operations = [op for op in self.operations if op.name != name]
        return self

    def get_operation(self, name: SnakeString) -> MethodSpec:
        """Get a MethodSpec operation by name. Raises ValueError if not found."""
        for op in self.operations:
            if op.name == name:
                return op
        raise ValueError(f"Operation '{name}' not found in port '{self.name}'")
