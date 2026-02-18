from typing import Iterable

from codegen.domain_definition.domain.value_objects.value_object_spec import (
    ValueObjectSpec,
)
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


@dataclass
class ValueObjectMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, value_object: ValueObjectSpec) -> ModuleSpec:

        attributes = [
            self.attribute_mapper.to_variable_spec(
                attr, default_field_flavor=FieldFlavor.PYDANTIC
            )
            for attr in value_object.attributes
        ]
        methods = []
        for method in value_object.behaviors:
            if method.inputs and method.inputs[0].name == "cls":
                func_type = FunctionType.CLASS_METHOD
            elif method.inputs and method.inputs[0].name == "self":
                func_type = FunctionType.INSTANCE_METHOD
            else:
                func_type = FunctionType.INSTANCE_METHOD
            func_spec = self.method_mapper.to_function_spec(
                method=method,
                function_type=func_type,
            )
            methods.append(func_spec)
        class_spec = ClassSpec.create(
            name=value_object.name,
            description=value_object.description,
            inheritance=["ValueObject"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=value_object.name, classes=[class_spec])

    def to_package_spec(self, value_objects: Iterable[ValueObjectSpec]) -> PackageSpec:
        modules = [self.to_module_spec(vo) for vo in value_objects]
        return PackageSpec.create(
            name="value_objects",
            modules=modules,
        )

    def module_spec_to_value_objects(
        self, module_spec: ModuleSpec
    ) -> list[ValueObjectSpec]:
        value_objects: list[ValueObjectSpec] = []
        for cls in module_spec.classes:
            attrs = [
                self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
            ]
            behaviors = [self.method_mapper.to_method(m) for m in cls.methods]
            vo = ValueObjectSpec(
                name=cls.name,
                description=cls.description,
                attributes=attrs,
                behaviors=behaviors,
            )
            value_objects.append(vo)
        return value_objects

    def to_value_objects(self, package_spec: PackageSpec) -> list[ValueObjectSpec]:
        value_objects: list[ValueObjectSpec] = []
        if package_spec.name != "value_objects":
            return []
        for module in package_spec.modules:
            if module.is_init_module():
                continue
            value_objects.extend(self.module_spec_to_value_objects(module))
        return value_objects
