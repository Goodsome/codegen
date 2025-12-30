from typing import Iterable

from codegen.domain_definition.domain.value_objects.meta_value_object import (
    MetaValueObject,
)
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


@dataclass
class ValueObjectMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, value_object: MetaValueObject) -> ModuleSpec:
        from codegen.python_gen.domain.value_objects.parameter_spec import FieldFlavor

        attributes = [
            self.attribute_mapper.to_parameter_spec(
                attr, default_field_flavor=FieldFlavor.PYDANTIC
            )
            for attr in value_object.attributes
        ]
        class_spec = ClassSpec.create(
            name=value_object.name,
            description=value_object.description,
            inheritance=["ValueObject"],
            attributes=attributes,
        )
        return ModuleSpec.create(name=value_object.name, classes=[class_spec])

    def to_package_spec(self, value_objects: Iterable[MetaValueObject]) -> PackageSpec:
        modules = [self.to_module_spec(vo) for vo in value_objects]
        return PackageSpec.create(
            name="value_objects",
            modules=modules,
        )

    def to_value_object(self, module_spec: ModuleSpec) -> MetaValueObject:
        cls = module_spec.classes[0]
        attributes = [
            self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
        ]
        return MetaValueObject(
            name=cls.name,
            description=cls.description,
            attributes=attributes,
        )

    def to_value_objects(self, package_spec: PackageSpec) -> list[MetaValueObject]:
        if package_spec.name != "value_objects":
            return []
        return [self.to_value_object(module) for module in package_spec.modules]
