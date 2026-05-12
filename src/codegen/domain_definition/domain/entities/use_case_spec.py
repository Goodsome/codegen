from __future__ import annotations

from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.core.attribute_spec_list import AttributeSpecList
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.core import Entity
from codegen.domain_definition.domain.core.method_spec_list import MethodSpecList
from codegen.shared.domain.value_objects.snake_string import SnakeString


class UseCaseSpec(Entity):
    """Specification of a use case to be generated."""

    name: PascalString
    description: str = Field(default_factory=str)
    attributes: AttributeSpecList = Field(default_factory=AttributeSpecList)
    behaviors: MethodSpecList = Field(default_factory=MethodSpecList)

    def get_input_name(self: Self) -> str:
        execute_behavior = self.behaviors.get(SnakeString("execute"))
        attr = execute_behavior.inputs[1]
        return attr.type

    def get_result_name(self: Self) -> str:
        execute_behavior = self.behaviors.get(SnakeString("execute"))
        return execute_behavior.output.type

    def to_class_spec(self: Self) -> ClassSpec:
        vs = self.attributes.to_variable_specs(flavor=FieldFlavor.DATACLASS)
        fs = self.behaviors.to_function_specs()
        return ClassSpec.create(
            name=self.name,
            description=self.description,
            attributes=vs,
            methods=fs,
            decorators=["dataclass"]
        )
        
    def to_module_spec(self) -> ModuleSpec:
        """将 UseCaseSpec 转换为 ModuleSpec"""
        cs = self.to_class_spec()
        return ModuleSpec.create(name=self.name, classes=[cs])


    @classmethod
    def from_class_spec(cls: type[Self], class_spec: ClassSpec) -> Self:
        attributes = AttributeSpecList.from_variable_specs(class_spec.attributes)
        behaviors = MethodSpecList.from_function_specs(class_spec.methods)
        return cls(
            name=class_spec.name,
            description=class_spec.description,
            attributes=attributes,
            behaviors=behaviors,
        )
        
    @classmethod
    def from_module_spec(cls: type[Self], module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 DomainConcept"""
        cls_spec = module.get_class(
            class_name=module.name,
        )
        return cls.from_class_spec(cls_spec)

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create test package for entity with behaviors that have rules."""
        tms = self.behaviors.to_test_modules()
        p = PackageSpec.create(name=self.name, modules=tms)
        return PackageSpec.create(
            name="use_cases",
            sub_packages=[p],
        )
        
        
    def load_test_package(self: Self, test_pkg: PackageSpec) -> Self:
        """Load test package into the domain concept. Returns self for chaining."""
        for module in test_pkg.modules:
            for behavior in self.behaviors:
                test_module_name = f"test_{behavior.name.to_snake()}"
                if module.name == test_module_name:
                    behavior.load_test_module(module)

        return self
