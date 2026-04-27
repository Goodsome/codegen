from typing import Iterable, Self

from pydantic import Field

from codegen.domain_definition.domain.core.method_spec_list import MethodSpecList
from codegen.domain_definition.domain.enums import PortType
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.core import Entity


class PortSpec(Entity):
    """Specification of a domain port to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    kind: PortType
    operations: MethodSpecList = Field(default_factory=MethodSpecList)

    @classmethod
    def create(
        cls,
        name: str,
        kind: PortType | str,
        description: str = "",
        operations: list[MethodSpec] | None = None,
    ) -> Self:
        if isinstance(kind, str):
            kind = PortType(kind)
        return cls(
            name=PascalString(name),
            kind=kind,
            description=description,
            operations=MethodSpecList(root=operations or []),
        )

    def to_module_spec(self) -> ModuleSpec:
        """将 PortSpec 转换为 ModuleSpec"""
        methods = [
            method.to_function_spec()
            for method in self.operations
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
        operations = MethodSpecList.from_function_specs(cls_spec.methods)
        if "Repository" in cls_spec.name:
            kind = "repository"
        elif cls_spec.name in ["UnitOfWork"]:
            kind = "repository"
        else:
            kind = "adapter"
        return cls.create(
            name=cls_spec.name,
            kind=kind,
            description=cls_spec.description,
            operations=operations.root,
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

    def update(
        self,
        kind: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if description is not None:
            self.description = description
        if kind is not None:
            self.kind = PortType(kind)

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create test package for port with operations that have rules."""
        tms = self.operations.to_test_modules()
        p = PackageSpec.create(name=str(self.name), modules=tms)
        return PackageSpec.create(
            name="ports",
            sub_packages=[p],
        )
