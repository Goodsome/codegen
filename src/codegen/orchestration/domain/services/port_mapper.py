from dataclasses import dataclass, field
from typing import Iterable

from codegen.domain_definition.domain.value_objects.meta_port import MetaPort
from codegen.orchestration.domain.services.attribute_mapper import AttributeMapper
from codegen.orchestration.domain.services.method_mapper import MethodMapper
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionType
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec


@dataclass
class PortMapper:

    attribute_mapper: AttributeMapper = field(default_factory=AttributeMapper)
    method_mapper: MethodMapper = field(default_factory=MethodMapper)

    def to_module_spec(self, port: MetaPort) -> ModuleSpec:
        methods = [
            self.method_mapper.to_function_spec(
                method, function_type=FunctionType.INSTANCE_METHOD
            )
            for method in port.operations
        ]
        # 端口通常是抽象基类
        class_spec = ClassSpec.create(
            name=port.name,
            description=port.description,
            inheritance=["ABC"],
            methods=methods,
        )
        return ModuleSpec.create(name=port.name, classes=[class_spec])

    def to_package_spec(self, ports: Iterable[MetaPort]) -> PackageSpec:
        modules = []
        for port in ports:
            modules.append(self.to_module_spec(port))
        return PackageSpec.create(
            name="ports",
            modules=modules,
        )

    def to_port(self, module_spec: ModuleSpec) -> MetaPort:
        cls = module_spec.classes[0]
        operations = [self.method_mapper.to_method(method) for method in cls.methods]
        return MetaPort(
            name=cls.name,
            description=cls.description,
            kind="Repository" if "Repository" in cls.name else "Service",
            operations=operations,
        )

    def to_ports(self, package_spec: PackageSpec) -> list[MetaPort]:
        if package_spec.name != "ports":
            return []
        return [self.to_port(module) for module in package_spec.modules]
