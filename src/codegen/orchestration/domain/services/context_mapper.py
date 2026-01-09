from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.shared.domain.services.naming_service import NamingService
from dataclasses import field
from codegen.orchestration.domain.services.domain_mapper import DomainMapper
from codegen.orchestration.domain.services.application_mapper import ApplicationMapper
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.orchestration.domain.services.infrastructure_mapper import (
    InfrastructureMapper,
)


@dataclass
class ContextMapper:

    domain_mapper: DomainMapper = field(default_factory=DomainMapper)
    application_mapper: ApplicationMapper = field(default_factory=ApplicationMapper)
    infrastructure_mapper: InfrastructureMapper = field(
        default_factory=InfrastructureMapper
    )

    def to_package_spec(self, context: BoundedContext) -> PackageSpec:
        domain_pkg = self.domain_mapper.to_package_spec(context.domain)
        application_pkg = self.application_mapper.to_package_spec(context.application)
        class_specs: dict[str, ClassSpec] = {}
        self._collect_class_specs_in_ports(class_specs, domain_pkg)
        self._collect_class_specs_in_ports(class_specs, application_pkg)
        infrastructure_pkg = self.infrastructure_mapper.to_package_spec(
            infrastructure=context.infrastructure,
            port_finder=context.get_port_spec,
        )
        if NamingService().to_snake_case(context.name) == "shared":
            modules = [ModuleSpec.create_shared_models()]
        else:
            modules = []

        return PackageSpec.create(
            name=context.name,
            sub_packages=[domain_pkg, application_pkg, infrastructure_pkg],
            modules=modules,
        )

    def to_context(self, package_spec: PackageSpec) -> BoundedContext:
        domain = None
        application = None
        infrastructure = None
        for pkg in package_spec.sub_packages:
            if pkg.name == "domain":
                domain = self.domain_mapper.to_domain(pkg)
            elif pkg.name == "application":
                application = self.application_mapper.to_application(pkg)
            elif pkg.name == "infrastructure":
                infrastructure = self.infrastructure_mapper.to_infrastructure(pkg)
        context_name = NamingService().to_camel_case(package_spec.name)
        return BoundedContext.create(
            name=context_name,
            domain=domain,
            application=application,
            infrastructure=infrastructure,
        )

    def _collect_class_specs_in_ports(
        self, class_specs: dict[str, ClassSpec], package_spec: PackageSpec
    ) -> None:
        if package_spec.name == "ports":
            class_specs.update(package_spec.collect_class_spec())
        else:
            for pkg in package_spec.sub_packages:
                self._collect_class_specs_in_ports(class_specs, pkg)
