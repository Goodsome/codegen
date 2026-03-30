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


class ValueObjectSpec(Entity):
    """Specification of a value object to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    behaviors: list[MethodSpec] = Field(default_factory=list)

    def to_module_spec(self) -> ModuleSpec:
        """将 ValueObjectSpec 转换为 ModuleSpec"""
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
                type=func_type,
                class_name=str(self.name),
            )
            methods.append(func_spec)
        class_spec = ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=["ValueObject"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def to_package_spec(cls, value_objects: Iterable[Self]) -> PackageSpec:
        """将多个 ValueObjectSpec 转换为一个 'value_objects' 包"""
        modules = [vo.to_module_spec() for vo in value_objects]
        return PackageSpec.create(name="value_objects", modules=modules)

    @classmethod
    def from_module_spec(cls, module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 ValueObjectSpec"""
        cls_spec = module.classes[0]
        attrs = [
            AttributeSpec.from_variable_spec(attr) for attr in cls_spec.attributes
        ]
        behaviors = [MethodSpec.from_function_spec(m) for m in cls_spec.methods]
        return cls(
            name=cls_spec.name,
            description=cls_spec.description,
            attributes=attrs,
            behaviors=behaviors,
        )

    @classmethod
    def from_package_spec(cls, package: PackageSpec) -> list[Self]:
        """将 'value_objects' 包逆向解析为 ValueObjectSpec 列表"""
        if package.name != "value_objects":
            return []
        value_objects: list[Self] = []
        for module in package.modules:
            if module.is_init_module():
                continue
            value_objects.append(cls.from_module_spec(module))
        return value_objects

    def update_metadata(self, description: str) -> None:
        """Update scalar metadata fields (e.g., description). Preserves internal structure."""
        self.description = description

    def add_attribute(self, attribute: AttributeSpec) -> Self:
        """Add an AttributeSpec. Raises ValueError if attribute with same name exists."""
        for attr in self.attributes:
            if attr.name == attribute.name:
                raise ValueError(f"Attribute '{attribute.name}' already exists in value_object '{self.name}'")
        self.attributes.append(attribute)
        return self

    def update_attribute(self, attribute: AttributeSpec) -> Self:
        """Update an existing AttributeSpec by name. Raises ValueError if not found."""
        for i, attr in enumerate(self.attributes):
            if attr.name == attribute.name:
                self.attributes[i] = attribute
                return self
        raise ValueError(f"Attribute '{attribute.name}' not found in value_object '{self.name}'")

    def remove_attribute(self, name: SnakeString) -> Self:
        """Remove an AttributeSpec by name. Returns self for chaining."""
        self.attributes = [attr for attr in self.attributes if attr.name != name]
        return self

    def get_attribute(self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec by name. Raises ValueError if not found."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        raise ValueError(f"Attribute '{name}' not found in value_object '{self.name}'")

    def add_behavior(self, behavior: MethodSpec) -> Self:
        """Add a MethodSpec behavior. Raises ValueError if behavior with same name exists."""
        for beh in self.behaviors:
            if beh.name == behavior.name:
                raise ValueError(f"Behavior '{behavior.name}' already exists in value_object '{self.name}'")
        self.behaviors.append(behavior)
        return self

    def update_behavior(self, behavior: MethodSpec) -> Self:
        """Update an existing MethodSpec behavior by name. Raises ValueError if not found."""
        for i, beh in enumerate(self.behaviors):
            if beh.name == behavior.name:
                self.behaviors[i] = behavior
                return self
        raise ValueError(f"Behavior '{behavior.name}' not found in value_object '{self.name}'")

    def remove_behavior(self, name: SnakeString) -> Self:
        """Remove a MethodSpec behavior by name. Returns self for chaining."""
        self.behaviors = [beh for beh in self.behaviors if beh.name != name]
        return self

    def get_behavior(self, name: SnakeString) -> MethodSpec:
        """Get a MethodSpec behavior by name. Raises ValueError if not found."""
        for beh in self.behaviors:
            if beh.name == name:
                return beh
        raise ValueError(f"Behavior '{name}' not found in value_object '{self.name}'")
