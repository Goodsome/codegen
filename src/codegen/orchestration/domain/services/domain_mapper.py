from dataclasses import field
from codegen.domain_definition.domain.value_objects.meta_domain import MetaDomain
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

    def to_package_spec(self, domain: MetaDomain) -> PackageSpec:
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
        return PackageSpec.create(
            name="domain",
            sub_packages=sub_packages,
        )

    def to_domain(self, package_spec: PackageSpec) -> MetaDomain:
        aggregates = []
        value_objects = []
        services = []
        ports = []

        for pkg in package_spec.sub_packages:
            if pkg.name == "aggregates":
                aggregates = self.aggregate_mapper.to_aggregates(pkg)
            elif pkg.name == "value_objects":
                value_objects = self.value_object_mapper.to_value_objects(pkg)
            elif pkg.name == "services":
                services = self.service_mapper.to_services(pkg)
            elif pkg.name == "ports":
                ports = self.port_mapper.to_ports(pkg)

        return MetaDomain(
            aggregates=aggregates,
            value_objects=value_objects,
            services=services,
            ports=ports,
        )
