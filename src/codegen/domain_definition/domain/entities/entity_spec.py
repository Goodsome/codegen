from typing import Iterable, Self

from pydantic import Field

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import Entity


class EntitySpec(Entity):
    """Specification of an entity."""

    name: PascalString
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    behaviors: list[MethodSpec] = Field(default_factory=list)

    def to_module_spec(self) -> ModuleSpec:
        """将 EntitySpec 转换为 ModuleSpec"""
        attributes = [
            attr.to_variable_spec(flavor=FieldFlavor.PYDANTIC)
            for attr in self.attributes
        ]
        methods = [
            method.to_function_spec(
                type=FunctionType.INSTANCE_METHOD,
                class_name=str(self.name),
            )
            for method in self.behaviors
        ]
        class_spec = ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=["Entity"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def to_package_spec(cls, entities: Iterable[Self]) -> PackageSpec:
        """将多个 EntitySpec 转换为一个 'entities' 包"""
        modules = [entity.to_module_spec() for entity in entities]
        return PackageSpec.create(name="entities", modules=modules)

    @classmethod
    def from_module_spec(cls, module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 EntitySpec"""
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
    def from_package_spec(cls, package: PackageSpec) -> list[Self]:
        """将 'entities' 包逆向解析为 EntitySpec 列表"""
        if package.name != "entities":
            return []
        entities: list[Self] = []
        for module in package.modules:
            if module.is_init_module():
                continue
            entities.append(cls.from_module_spec(module))
        return entities

    def update_metadata(self, description: str) -> None:
        """Update scalar metadata fields (e.g., description). Preserves internal structure."""
        self.description = description
    