from codegen.orchestration.domain.services.enum_mapper import EnumMapper
from codegen.domain_definition.domain.value_objects.enum_spec import EnumSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from dataclasses import field
from codegen.domain_definition.domain.value_objects.domain_spec import DomainSpec
from codegen.orchestration.domain.services.port_mapper import PortMapper
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass
from codegen.orchestration.domain.services.value_object_mapper import ValueObjectMapper
from codegen.orchestration.domain.services.service_mapper import ServiceMapper
from codegen.orchestration.domain.services.aggregate_mapper import AggregateMapper


@dataclass
class DomainMapper:

    aggregate_mapper: AggregateMapper = field(default_factory=AggregateMapper)
    value_object_mapper: ValueObjectMapper = field(default_factory=ValueObjectMapper)
    service_mapper: ServiceMapper = field(default_factory=ServiceMapper)
    port_mapper: PortMapper = field(default_factory=PortMapper)
    enum_mapper: EnumMapper = field(default_factory=EnumMapper)

    def to_package_spec(self, domain: DomainSpec) -> PackageSpec:
        aggregate_pkg = self.aggregate_mapper.to_package_spec(domain.aggregates)
        value_objects_pkg = self.value_object_mapper.to_package_spec(
            domain.value_objects
        )
        services_pkg = self.service_mapper.to_package_spec(domain.services)
        ports_pkg = self.port_mapper.to_package_spec(domain.ports)
        sub_packages = [
            aggregate_pkg,
            value_objects_pkg,
            services_pkg,
            ports_pkg,
        ]
        modules: list[ModuleSpec] = []
        if domain.enums:
            modules.append(self.enum_mapper.to_module_spec(domain.enums))
        return PackageSpec.create(
            name="domain",
            sub_packages=sub_packages,
            modules=modules,
        )

    def to_domain(self, package_spec: PackageSpec) -> DomainSpec:
        aggregates = []
        value_objects = []
        services = []
        ports = []
        enums: list[EnumSpec] = []

        for pkg in package_spec.sub_packages:
            if pkg.name == "aggregates":
                aggregates = self.aggregate_mapper.to_aggregates(pkg)
            elif pkg.name == "value_objects":
                value_objects = self.value_object_mapper.to_value_objects(pkg)
            elif pkg.name == "services":
                services = self.service_mapper.to_services(pkg)
            elif pkg.name == "ports":
                ports = self.port_mapper.to_ports(pkg)
        for module in package_spec.modules:
            if module.name == "enums":
                enums = list(self.enum_mapper.to_meta_enums(module))

        return DomainSpec(
            aggregates=aggregates,
            value_objects=value_objects,
            services=services,
            ports=ports,
            enums=enums,
        )
