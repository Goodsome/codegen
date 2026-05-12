from __future__ import annotations

from typing import Self

from pydantic import Field

from codegen.domain_definition.domain.core.attribute_spec_list import AttributeSpecList
from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.core import Entity
from codegen.domain_definition.domain.core.method_spec_list import MethodSpecList


class UseCaseSpec(Entity):
    """Specification of a use case to be generated."""

    name: PascalString
    kind: UseCaseKind
    inputs: AttributeSpecList = Field(default_factory=AttributeSpecList)
    outputs: AttributeSpecList = Field(default_factory=AttributeSpecList)
    description: str = Field(default_factory=str)
    attributes: AttributeSpecList = Field(default_factory=AttributeSpecList)
    behaviors: MethodSpecList = Field(default_factory=MethodSpecList)

    def to_class_spec(self: Self) -> ClassSpec:
        vs = self.attributes.to_variable_specs(flavor=FieldFlavor.DATACLASS)
        fs = self.behaviors.to_function_specs()
        return ClassSpec.create(
            name=self.name,
            description=self.description,
            attributes=vs,
            methods=fs,
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
            kind=UseCaseKind.COMMAND,
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

    def update(
        self, kind: str | UseCaseKind | None = None, description: str | None = None
    ) -> Self:
        """Update scalar metadata fields. Preserves internal structure."""
        if kind is not None:
            if isinstance(kind, str):
                kind = UseCaseKind(kind)
            self.kind = kind
        if description is not None:
            self.description = description
        return self
