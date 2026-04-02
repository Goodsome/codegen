from typing import Iterable, Self, Union
from codegen.shared.models import Entity
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.enums import FieldFlavor, FunctionType
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.domain_definition.domain.core.has_attributes import HasAttributes
from codegen.domain_definition.domain.core.has_behaviors import HasBehaviors
from pydantic import Field

class CoreSpec(Entity, HasAttributes, HasBehaviors):
    """Specification of a core entity to be generated."""

    name: PascalString
    description: str

    def to_module_spec(self: Self) -> ModuleSpec:
        """将 AggregateSpec 转换为 ModuleSpec"""
        attributes = [
            attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
            for attr in self.attributes
        ]
        methods = []
        for method in self.behaviors:
            if method.inputs and method.inputs[0].name == "cls":
                func_type = FunctionType.CLASS_METHOD
            else:
                func_type = FunctionType.INSTANCE_METHOD
            func_spec = method.to_function_spec(
                type=func_type, class_name=str(self.name)
            )
            methods.append(func_spec)
        class_spec = ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=["BaseModel"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def to_package_spec(cls: type[Self], aggregates: Iterable[Self]) -> PackageSpec:
        """将多个 base_model 转换为一个 'core' 包"""
        modules = [agg.to_module_spec() for agg in aggregates]
        return PackageSpec.create(name="core", modules=modules)

    @classmethod
    def from_module_spec(cls: type[Self], module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 AggregateSpec"""
        cls_spec = module.classes[0]
        attributes = [
            AttributeSpec.from_variable_spec(attr) for attr in cls_spec.attributes
        ]
        behaviors = [
            MethodSpec.from_function_spec(method) for method in cls_spec.methods
        ]
        return cls(
            name=cls_spec.name,
            description=cls_spec.description,
            attributes=attributes,
            behaviors=behaviors,
        )

    @classmethod
    def from_package_spec(cls: type[Self], package: PackageSpec) -> list[Self]:
        """将 'aggregates' 包逆向解析为 AggregateSpec 列表"""
        if package.name != "core":
            return []
        aggregates: list[Self] = []
        for module in package.modules:
            if module.is_init_module():
                continue
            aggregates.append(cls.from_module_spec(module))
        return aggregates

    def update(self: Self, description: str | None = None) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if description is not None:
            self.description = description

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create test package for aggregate with behaviors that have rules."""
        modules = []
        for behavior in self.behaviors:
            tm = behavior.to_test_module_spec()
            bm = behavior.to_bindings_module_spec()
            if tm.functions:
                modules.append(tm)
                modules.append(bm)
        p = PackageSpec.create(name=str(self.name), modules=modules)
        return PackageSpec.create(
            name="core",
            sub_packages=[p],
        )
