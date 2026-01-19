from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from typing import Iterable
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.enums import FunctionType, FieldFlavor


@dataclass
class ServiceMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, service: ServiceSpec) -> ModuleSpec:
        attributes = [
            self.attribute_mapper.to_parameter_spec(
                attr,
                default_field_flavor=FieldFlavor.DATACLASS,
            )
            for attr in service.dependencies
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

    def to_package_spec(self, services: Iterable[ServiceSpec]) -> PackageSpec:
        modules = [self.to_module_spec(s) for s in services]
        return PackageSpec.create(
            name="services",
            modules=modules,
        )

    def to_service(self, module_spec: ModuleSpec) -> ServiceSpec:
        cls = module_spec.classes[0]
        attributes = [
            self.attribute_mapper.to_attribute(attr) for attr in cls.attributes
        ]
        operations = [self.method_mapper.to_method(method) for method in cls.methods]
        return ServiceSpec(
            name=cls.name,
            description=cls.description,
            dependencies=attributes,
            operations=operations,
        )

    def to_services(self, package_spec: PackageSpec) -> list[ServiceSpec]:
        services: list[ServiceSpec] = []
        if package_spec.name != "services":
            return services
        for module in package_spec.modules:
            if module.is_init_module():
                continue
            services.append(self.to_service(module))
        return services
