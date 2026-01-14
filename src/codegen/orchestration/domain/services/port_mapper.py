from dataclasses import dataclass, field
from typing import Iterable

from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


@dataclass
class PortMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, port: PortSpec) -> ModuleSpec:
        methods = [
            self.method_mapper.to_function_spec(
                method,
                function_type=FunctionType.INSTANCE_METHOD,
                is_abstract=True,
            )
            for method in port.get_final_operations()
        ]
        class_spec = ClassSpec.create(
            name=port.name,
            description=port.description,
            inheritance=["ABC"],
            methods=methods,
        )
        return ModuleSpec.create(name=port.name, classes=[class_spec])

    def to_package_spec(self, ports: Iterable[PortSpec]) -> PackageSpec:
        modules = []
        for port in ports:
            modules.append(self.to_module_spec(port))
        return PackageSpec.create(
            name="ports",
            modules=modules,
        )

    def to_port(self, module_spec: ModuleSpec) -> PortSpec:
        cls = module_spec.classes[0]
        operations = [self.method_mapper.to_method(method) for method in cls.methods]
        return PortSpec.create(
            name=cls.name,
            kind="repository" if "Repository" in cls.name else "adapter",
            description=cls.description,
            operations=operations,
        )

    def to_ports(self, package_spec: PackageSpec) -> list[PortSpec]:
        ports: list[PortSpec] = []
        if package_spec.name != "ports":
            return ports
        for module in package_spec.modules:
            if module.is_init_module():
                continue
            ports.append(self.to_port(module))
        return ports
