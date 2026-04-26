from typing import ClassVar, Iterable, Self

from pydantic import BaseModel, Field

from codegen.domain_definition.domain.core.attribute_spec_list import AttributeSpecList
from codegen.domain_definition.domain.core.method_spec_list import MethodSpecList
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString


class DomainConcept(BaseModel):
    """Specification of a core entity to be generated."""

    name: PascalString
    description: str
    base_types: list[str] = Field(default_factory=list)
    attributes: AttributeSpecList = Field(default_factory=AttributeSpecList)
    behaviors: MethodSpecList = Field(default_factory=MethodSpecList)

    __concept_name__: ClassVar[str]
    __pkg_name__: ClassVar[str]

    @property
    def entity_name(self) -> str:
        return str(self.name)

    def to_module_spec(self: Self) -> ModuleSpec:
        """将 DomainConcept 转换为 ModuleSpec"""
        vs = self.attributes.to_variable_specs(flavor=FieldFlavor.PYDANTIC)
        fs = self.behaviors.to_function_specs()
        if self.__concept_name__ != "core":
            base_types = [PascalString(self.__concept_name__)] + self.base_types
        else:
            base_types = self.base_types
        class_spec = ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=base_types,
            attributes=vs,
            methods=fs,
        )
        return ModuleSpec.create(name=self.name, classes=[class_spec])

    @classmethod
    def from_module_spec(cls: type[Self], module: ModuleSpec) -> Self:
        """将 ModuleSpec 逆向解析为 DomainConcept"""
        cls_spec = module.classes[0]
        attributes = AttributeSpecList.from_variable_specs(cls_spec.attributes)
        behaviors = MethodSpecList.from_function_specs(cls_spec.methods)
        base_types = [
            i
            for i in cls_spec.inheritance
            if i not in ["Entity", "ValueObject", "AggregateRoot", "DomainEvent", "DomainException", "Repository"]
        ]
        return cls(
            name=cls_spec.name,
            description=cls_spec.description,
            base_types=base_types,
            attributes=attributes,
            behaviors=behaviors,
        )

    @classmethod
    def to_package_spec(cls: type[Self], domain_concept: Iterable[Self]) -> PackageSpec:
        """将多个 DomainConcept 转换为一个 'core' 包"""
        modules = [dc.to_module_spec() for dc in domain_concept]
        return PackageSpec.create(name=cls.__pkg_name__, modules=modules)

    @classmethod
    def from_package_spec(cls: type[Self], package: PackageSpec) -> list[Self]:
        """将 PackageSpec 包逆向解析为 DomainConcept 列表"""
        if package.name != cls.__pkg_name__:
            return []
        aggregates: list[Self] = []
        for module in package.modules:
            if module.is_init_module():
                continue
            aggregates.append(cls.from_module_spec(module))
        return aggregates

    def to_test_package_spec(self: Self) -> PackageSpec:
        """Create test package for entity with behaviors that have rules."""
        tms = self.behaviors.to_test_modules()
        p = PackageSpec.create(name=self.entity_name, modules=tms)
        return PackageSpec.create(
            name=self.__pkg_name__,
            sub_packages=[p],
        )

    def update(
        self: Self,
        description: str | None = None,
        base_types: list[str] | None = None,
    ) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if description is not None:
            self.description = description
        if base_types is not None:
            self.base_types = base_types

    def load_test_package(self: Self, test_pkg: PackageSpec) -> Self:
        """Load test package into the domain concept. Returns self for chaining."""
        for module in test_pkg.modules:
            # Load test cases into corresponding behaviors
            for behavior in self.behaviors:
                test_module_name = f"test_{behavior.name.to_snake()}"
                if module.name == test_module_name:
                    behavior.load_test_module(module)

        return self
