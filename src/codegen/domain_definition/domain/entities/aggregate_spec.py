from typing import Iterable, Self, Union
from pydantic import Field
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.python_gen.domain.enums import FieldFlavor, FunctionType
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity


class AggregateSpec(Entity):
    """Specification of a domain aggregate to be generated."""

    name: PascalString
    description: str
    attributes: list[AttributeSpec] = Field(default_factory=list)
    behaviors: list[MethodSpec] = Field(default_factory=list)

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
            inheritance=["AggregateRoot"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def to_package_spec(cls: type[Self], aggregates: Iterable[Self]) -> PackageSpec:
        """将多个 AggregateSpec 转换为一个 'aggregates' 包"""
        modules = [agg.to_module_spec() for agg in aggregates]
        return PackageSpec.create(name="aggregates", modules=modules)

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
        if package.name != "aggregates":
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

    def add_attribute(self: Self, attribute: AttributeSpec) -> Self:
        """Add an AttributeSpec. Raises ValueError if attribute with same name exists."""
        for attr in self.attributes:
            if attr.name == attribute.name:
                raise ValueError(
                    f"Attribute '{attribute.name}' already exists in aggregate '{self.name}'"
                )
        self.attributes.append(attribute)
        return self

    def update_attribute(self: Self, attribute: AttributeSpec) -> Self:
        """Update an existing AttributeSpec by name. Raises ValueError if not found."""
        for i, attr in enumerate(self.attributes):
            if attr.name == attribute.name:
                self.attributes[i] = attribute
                return self
        raise ValueError(
            f"Attribute '{attribute.name}' not found in aggregate '{self.name}'"
        )

    def remove_attribute(self: Self, name: SnakeString) -> Self:
        """Remove an AttributeSpec by name. Returns self for chaining."""
        self.attributes = [attr for attr in self.attributes if attr.name != name]
        return self

    def get_attribute(self: Self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec by name. Raises ValueError if not found."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        raise ValueError(f"Attribute '{name}' not found in aggregate '{self.name}'")

    def add_behavior(self: Self, behavior: MethodSpec) -> Self:
        """Add a MethodSpec behavior. Raises ValueError if behavior with same name exists."""
        for beh in self.behaviors:
            if beh.name == behavior.name:
                raise ValueError(
                    f"Behavior '{behavior.name}' already exists in aggregate '{self.name}'"
                )
        self.behaviors.append(behavior)
        return self

    def update_behavior(self: Self, behavior: MethodSpec) -> Self:
        """Update an existing MethodSpec behavior by name. Raises ValueError if not found."""
        for i, beh in enumerate(self.behaviors):
            if beh.name == behavior.name:
                self.behaviors[i] = behavior
                return self
        raise ValueError(
            f"Behavior '{behavior.name}' not found in aggregate '{self.name}'"
        )

    def remove_behavior(self: Self, name: SnakeString) -> Self:
        """Remove a MethodSpec behavior by name. Returns self for chaining."""
        self.behaviors = [beh for beh in self.behaviors if beh.name != name]
        return self

    def get_behavior(self: Self, name: SnakeString) -> MethodSpec:
        """Get a MethodSpec behavior by name. Raises ValueError if not found."""
        for beh in self.behaviors:
            if beh.name == name:
                return beh
        raise ValueError(f"Behavior '{name}' not found in aggregate '{self.name}'")

    def to_test_package_spec(self: Self) -> PackageSpec: ...
