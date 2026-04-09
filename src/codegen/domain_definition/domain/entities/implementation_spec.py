from typing import Self
from codegen.domain_definition.domain.core.attribute_spec_list import AttributeSpecList
from codegen.domain_definition.domain.core.method_spec_list import MethodSpecList
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.core import Entity
from pydantic import Field


class ImplementationSpec(Entity):
    """Specification of an implementation to be generated."""

    name: PascalString
    implements: PascalString
    technology: SnakeString
    description: str = Field(default_factory=str)
    attributes: AttributeSpecList = Field(default_factory=AttributeSpecList)
    private_methods: MethodSpecList = Field(default_factory=MethodSpecList)

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
            attributes=AttributeSpecList(root=attributes or []),
            private_methods=MethodSpecList(root=private_methods or []),
        )

    def to_module_spec(self, port: PortSpec) -> ModuleSpec:
        """将 ImplementationSpec 转换为 ModuleSpec（需要 port 获取 operations）"""
        port_ops = list(port.operations)
        methods = [
            f.to_function_spec() for f in port_ops
        ]
        methods += [
            f.to_function_spec()
            for f in self.private_methods
        ]

        attributes = self.attributes.to_variable_specs()
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
    def from_module_spec(
        cls, module_spec: ModuleSpec, technology: str
    ) -> "ImplementationSpec":
        """将 ModuleSpec 逆向解析为 ImplementationSpec"""
        for spec_cls in module_spec.classes:
            if spec_cls.inheritance:
                attributes = AttributeSpecList.from_variable_specs(spec_cls.attributes)
                private_methods_list = [
                    MethodSpec.from_function_spec(function)
                    for function in spec_cls.methods
                    if not function.is_init_method() and function.name.startswith("_") and not function.name.startswith("__")
                ]
                return cls.create(
                    name=spec_cls.name,
                    implements=spec_cls.inheritance[0],
                    technology=technology,
                    description=spec_cls.description,
                    attributes=attributes.root,
                    private_methods=private_methods_list,
                )
        raise ValueError(f"No Implementation found in module, {module_spec.name}")

    def _get_class_name(self) -> str:
        if self.name:
            return self.name
        return PascalString(self.technology) + self.implements

    def update(
        self,
        implements: str | None = None,
        technology: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if implements is not None:
            self.implements = PascalString(implements)
        if technology is not None:
            self.technology = SnakeString(technology)
        if description is not None:
            self.description = description

    def to_test_package_spec(self: Self, port: PortSpec) -> PackageSpec:
        """Create test package for implementation with operations that have rules."""
        tms = port.operations.to_test_modules()
        p = PackageSpec.create(name=str(self.name), modules=tms)
        return PackageSpec.create(
            name="implementations",
            sub_packages=[p],
        )

    def load_test_package(self: Self, test_pkg: PackageSpec, port: PortSpec) -> Self:
        """Load test package into the implementation spec. Returns self for chaining."""
        for module in test_pkg.modules:
            # Load test cases into corresponding port operations
            for method in port.operations:
                test_module_name = f"test_{method.name.to_snake()}"
                if module.name == test_module_name:
                    method.load_test_module(module)

        return self
