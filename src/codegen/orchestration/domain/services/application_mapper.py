from codegen.orchestration.domain.services.use_case_mapper import UseCaseMapper
from codegen.orchestration.domain.services.port_mapper import PortMapper
from codegen.domain_definition.domain.value_objects.application_spec import (
    ApplicationSpec,
)
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass, field


@dataclass
class ApplicationMapper:

    use_case_mapper: UseCaseMapper = field(default_factory=UseCaseMapper)
    port_mapper: PortMapper = field(default_factory=PortMapper)

    def to_package_spec(self, application: ApplicationSpec) -> PackageSpec:
        use_case_modules = [
            self.use_case_mapper.to_module_spec(uc) for uc in application.use_cases
        ]
        port_modules = [self.port_mapper.to_module_spec(p) for p in application.ports]

        use_cases_pkg = PackageSpec.create(name="use_cases", modules=use_case_modules)
        ports_pkg = PackageSpec.create(name="ports", modules=port_modules)

        return PackageSpec.create(
            name="application", sub_packages=[use_cases_pkg, ports_pkg]
        )

    def to_application(self, package_spec: PackageSpec) -> ApplicationSpec:
        use_cases = []
        ports = []

        for sub_pkg in package_spec.sub_packages:
            if sub_pkg.name == "use_cases":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        use_cases.append(self.use_case_mapper.to_use_case(mod))
            elif sub_pkg.name == "ports":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        ports.append(self.port_mapper.to_port(mod))

        return ApplicationSpec(use_cases=use_cases, ports=ports)
