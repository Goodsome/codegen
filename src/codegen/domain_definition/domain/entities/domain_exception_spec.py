from typing import override, Self
from codegen.domain_definition.domain.core.attribute_spec_list import AttributeSpecList
from codegen.domain_definition.domain.core.domain_concept import DomainConcept
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec

from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.shared.domain.core import Entity
from codegen.shared.domain.value_objects.pascal_string import PascalString

from codegen.python_gen.domain.value_objects.class_spec import ClassSpec


class DomainExceptionSpec(Entity, DomainConcept):
    """Specification of a domain exception to be generated."""

    __concept_name__ = "domain_exception"
    __pkg_name__ = "exceptions"

    @override
    def to_class_spec(self: Self) -> ClassSpec:
        base_types = [PascalString(self.__concept_name__)] + self.base_types
        im = self._get_init_methods()
        return ClassSpec.create(
            name=self.name,
            description=self.description,
            inheritance=base_types,
            methods=im,
        )

    @override
    @classmethod
    def from_class_spec(cls: type[Self], class_spec: ClassSpec) -> Self:
        attributes = cls._get_attributes(class_spec)
        base_types = [
            i
            for i in class_spec.inheritance
            if i not in ["Entity", "ValueObject", "AggregateRoot", "DomainEvent", "DomainException", "Repository"]
        ]
        return cls(
            name=class_spec.name,
            description=class_spec.description,
            attributes=attributes,
            base_types=base_types,
        )

    def _get_init_methods(self) -> list[FunctionSpec]:
        inputs: list[AttributeSpec] = [
            AttributeSpec.create(
                name="self",
                type="Self"
            )
        ] + self.attributes.root
        init_behavior = MethodSpec.create(
            name="__init__",
            inputs=inputs,
            output=MethodOutput(type="None")
        )
        fs = init_behavior.to_function_spec()
        return [fs]

    @classmethod
    def _get_attributes(cls: type[Self], class_spec: ClassSpec) -> AttributeSpecList:
        init_method = class_spec.find_method( method_name="__init__", )
        if init_method is None:
            return AttributeSpecList()
        return AttributeSpecList(
            root=[ 
                AttributeSpec.from_variable_spec(v) for v in init_method.parameters 
                if v.name not in ["self"] 
            ]
        )
