from codegen.python_gen.domain.value_objects.parameter_spec import FieldFlavor
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from typing import Iterable
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.meta_service import MetaService
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionType


@dataclass
class ServiceMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, service: MetaService) -> ModuleSpec:
        attributes = [
            self.attribute_mapper.to_parameter_spec(
                attr,
                default_field_flavor=FieldFlavor.DATACLASS,
            )
            for attr in service.attributes
        ]
        methods = [
            self.method_mapper.to_function_spec(
                method, function_type=FunctionType.INSTANCE_METHOD
            )
            for method in service.operations
        ]
        class_spec = ClassSpec.create(
            name=service.name,
            description=service.description,
            decorators=["dataclass"],
            attributes=attributes,
            methods=methods,
        )
        return ModuleSpec.create(name=service.name, classes=[class_spec])

    def to_package_spec(self, services: Iterable[MetaService]) -> PackageSpec:
        modules = [self.to_module_spec(s) for s in services]
        return PackageSpec.create(
            name="services",
            modules=modules,
        )

    def to_service(self, module_spec: ModuleSpec) -> MetaService:
        cls = module_spec.classes[0]
        attributes = [
            self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
        ]
        operations = [self.method_mapper.to_method(method) for method in cls.methods]
        return MetaService(
            name=cls.name,
            description=cls.description,
            attributes=attributes,
            operations=operations,
        )

    def to_services(self, package_spec: PackageSpec) -> list[MetaService]:
        if package_spec.name != "services":
            return []
        return [self.to_service(module) for module in package_spec.modules]
