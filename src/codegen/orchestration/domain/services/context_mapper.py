from codegen.orchestration.domain.services.domain_mapper import DomainMapper
from codegen.orchestration.domain.services.application_mapper import ApplicationMapper
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

    domain_mapper: DomainMapper
    application_mapper: ApplicationMapper
    infrastructure_mapper: InfrastructureMapper

    def to_package_spec(self, context: BoundedContext) -> PackageSpec:
        domain_pkg = self.domain_mapper.to_package_spec(context.domain)
        application_pkg = self.application_mapper.to_package_spec(context.application)
        infrastructure_pkg = self.infrastructure_mapper.to_package_spec(
            context.infrastructure
        )
        return PackageSpec.create(
            name=context.name,
            sub_packages=[domain_pkg, application_pkg, infrastructure_pkg],
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
        return BoundedContext.create(
            name=package_spec.name,
            domain=domain,
            application=application,
            infrastructure=infrastructure,
        )
