from typing import Callable, Self

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import Entity
from pydantic import Field


class ImplementationSpec(Entity):
    """Specification of an implementation to be generated."""

    name: PascalString
    implements: PascalString
    technology: SnakeString
    description: str = Field(default_factory=str)
    attributes: list[AttributeSpec] = Field(default_factory=list)
    private_methods: list[MethodSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        implements: str,
        technology: str,
        description: str = "",
        attributes: list[AttributeSpec] | None = None,
        private_methods: list[MethodSpec] | None = None,
    ):
        return cls(
            name=PascalString(name),
            implements=PascalString(implements),
            technology=SnakeString(technology),
            description=description,
            attributes=attributes or [],
            private_methods=private_methods or [],
        )

    def to_module_spec(self, port: PortSpec) -> ModuleSpec:
        """将 ImplementationSpec 转换为 ModuleSpec（需要 port 获取 operations）"""
        methods = [
            f.to_function_spec(type=FunctionType.INSTANCE_METHOD)
            for f in port.get_final_operations()
        ]
        methods += [
            f.to_function_spec(
                type=FunctionType.INSTANCE_METHOD,
                class_name=self._get_class_name(),
            )
            for f in self.private_methods
        ]
        for method in methods[len(port.get_final_operations()):]:
            method.is_private = True

        attributes = [
            attr.to_variable_spec()
            for attr in self.attributes
        ]
        class_name = self._get_class_name()
        class_spec = ClassSpec.create(
            name=class_name,
            decorators=["dataclass"],
            description=self.description,
            inheritance=[self.implements],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=class_name, classes=[class_spec])

    @classmethod
    def from_module_spec(cls, module_spec: ModuleSpec, technology: str) -> "ImplementationSpec":
        """将 ModuleSpec 逆向解析为 ImplementationSpec"""
        for spec_cls in module_spec.classes:
            if spec_cls.inheritance:
                attributes = [
                    AttributeSpec.from_variable_spec(attr) for attr in spec_cls.attributes
                ]
                private_methods: list[MethodSpec] = []
                for function in spec_cls.methods:
                    if function.is_init_method():
                        continue
                    if function.is_private:
                        private_methods.append(MethodSpec.from_function_spec(function))
                return cls.create(
                    name=spec_cls.name,
                    implements=spec_cls.inheritance[0],
                    technology=technology,
                    description=spec_cls.description,
                    attributes=attributes,
                    private_methods=private_methods,
                )
        raise ValueError(f"No Implementation found in module, {module_spec.name}")

    def _get_class_name(self) -> str:
        if self.name:
            return self.name
        return PascalString(self.technology) + self.implements

    def update_metadata(
        self,
        implements: str | None = None,
        technology: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update scalar metadata fields (e.g., implements, technology, description). Preserves internal structure."""
        if implements is not None:
            self.implements = PascalString(implements)
        if technology is not None:
            self.technology = SnakeString(technology)
        if description is not None:
            self.description = description

    def add_attribute(self, attribute: AttributeSpec) -> Self:
        """Add an AttributeSpec. Raises ValueError if attribute with same name exists."""
        for attr in self.attributes:
            if attr.name == attribute.name:
                raise ValueError(f"Attribute '{attribute.name}' already exists in implementation '{self.name}'")
        self.attributes.append(attribute)
        return self

    def update_attribute(self, attribute: AttributeSpec) -> Self:
        """Update an existing AttributeSpec by name. Raises ValueError if not found."""
        for i, attr in enumerate(self.attributes):
            if attr.name == attribute.name:
                self.attributes[i] = attribute
                return self
        raise ValueError(f"Attribute '{attribute.name}' not found in implementation '{self.name}'")

    def remove_attribute(self, name: SnakeString) -> Self:
        """Remove an AttributeSpec by name. Returns self for chaining."""
        self.attributes = [attr for attr in self.attributes if attr.name != name]
        return self

    def get_attribute(self, name: SnakeString) -> AttributeSpec:
        """Get an AttributeSpec by name. Raises ValueError if not found."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        raise ValueError(f"Attribute '{name}' not found in implementation '{self.name}'")

    def add_private_method(self, method: MethodSpec) -> Self:
        """Add a private MethodSpec. Raises ValueError if method with same name exists."""
        for m in self.private_methods:
            if m.name == method.name:
                raise ValueError(f"Private method '{method.name}' already exists in implementation '{self.name}'")
        self.private_methods.append(method)
        return self

    def update_private_method(self, method: MethodSpec) -> Self:
        """Update an existing private MethodSpec by name. Raises ValueError if not found."""
        for i, m in enumerate(self.private_methods):
            if m.name == method.name:
                self.private_methods[i] = method
                return self
        raise ValueError(f"Private method '{method.name}' not found in implementation '{self.name}'")

    def remove_private_method(self, name: SnakeString) -> Self:
        """Remove a private MethodSpec by name. Returns self for chaining."""
        self.private_methods = [m for m in self.private_methods if m.name != name]
        return self

    def get_private_method(self, name: SnakeString) -> MethodSpec:
        """Get a private MethodSpec by name. Raises ValueError if not found."""
        for m in self.private_methods:
            if m.name == name:
                return m
        raise ValueError(f"Private method '{name}' not found in implementation '{self.name}'")
