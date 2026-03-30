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

    def update(self, description: str | None = None) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if description is not None:
            self.description = description

    def add_attribute(self, attribute: AttributeSpec) -> Self:
        """Add an AttributeSpec. Raises ValueError if attribute with same name exists."""
        for attr in self.attributes:
            if attr.name == attribute.name:
                raise ValueError(f"Attribute '{attribute.name}' already exists in entity '{self.name}'")
        self.attributes.append(attribute)
        return self

    def update_attribute(self, attribute: AttributeSpec) -> Self:
        """Update an existing AttributeSpec by name. Raises ValueError if not found."""
        for i, attr in enumerate(self.attributes):
            if attr.name == attribute.name:
                self.attributes[i] = attribute
                return self
        raise ValueError(f"Attribute '{attribute.name}' not found in entity '{self.name}'")

    def remove_attribute(self, name: SnakeString) -> Self:
        """Remove an AttributeSpec by name. Returns self for chaining."""
        self.attributes = [attr for attr in self.attributes if attr.name != name]
        return self

    def get_attribute(self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec by name. Raises ValueError if not found."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        raise ValueError(f"Attribute '{name}' not found in entity '{self.name}'")

    def add_behavior(self, behavior: MethodSpec) -> Self:
        """Add a MethodSpec behavior. Raises ValueError if behavior with same name exists."""
        for beh in self.behaviors:
            if beh.name == behavior.name:
                raise ValueError(f"Behavior '{behavior.name}' already exists in entity '{self.name}'")
        self.behaviors.append(behavior)
        return self

    def update_behavior(self, behavior: MethodSpec) -> Self:
        """Update an existing MethodSpec behavior by name. Raises ValueError if not found."""
        for i, beh in enumerate(self.behaviors):
            if beh.name == behavior.name:
                self.behaviors[i] = behavior
                return self
        raise ValueError(f"Behavior '{behavior.name}' not found in entity '{self.name}'")

    def remove_behavior(self, name: SnakeString) -> Self:
        """Remove a MethodSpec behavior by name. Returns self for chaining."""
        self.behaviors = [beh for beh in self.behaviors if beh.name != name]
        return self

    def get_behavior(self, name: SnakeString) -> MethodSpec:
        """Get a MethodSpec behavior by name. Raises ValueError if not found."""
        for beh in self.behaviors:
            if beh.name == name:
                return beh
        raise ValueError(f"Behavior '{name}' not found in entity '{self.name}'")
    