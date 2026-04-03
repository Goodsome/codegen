from typing import Iterable, Self

from codegen.domain_definition.domain.core.attribute_spec_list import AttributeSpecList
from pydantic import Field

from codegen.domain_definition.domain.core.method_spec_list import MethodSpecList
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.core import Entity


class ServiceSpec(Entity):
    """Specification of a domain service to be generated."""

    name: PascalString
    description: str = ""
    dependencies: AttributeSpecList = Field(default_factory=AttributeSpecList)
    operations: MethodSpecList = Field(default_factory=MethodSpecList)

    def to_module_spec(self) -> ModuleSpec:
        """将 ServiceSpec 转换为 ModuleSpec"""
        attributes = self.dependencies.to_variable_specs(flavor=FieldFlavor.DATACLASS)
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
        dependencies = AttributeSpecList.from_variable_specs(cls_spec.attributes)
        operations = MethodSpecList.from_function_specs(cls_spec.methods)
        return cls(
            name=cls_spec.name,
            description=cls_spec.description,
            dependencies=dependencies,
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
