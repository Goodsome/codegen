from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.models import ValueObject
from pydantic import Field


class ApplicationSpec(ValueObject):
    """Specification of an application to be generated."""

    use_cases: list[UseCaseSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)

    def to_package_spec(self) -> PackageSpec:
        """将 ApplicationSpec 转换为 PackageSpec"""
        use_case_modules = [uc.to_module_spec() for uc in self.use_cases]
        port_modules = [p.to_module_spec() for p in self.ports]

        use_cases_pkg = PackageSpec.create(name="use_cases", modules=use_case_modules)
        ports_pkg = PackageSpec.create(name="ports", modules=port_modules)

        return PackageSpec.create(
            name="application", sub_packages=[use_cases_pkg, ports_pkg]
        )

    @classmethod
    def from_package_spec(cls, package_spec: PackageSpec) -> "ApplicationSpec":
        """将 PackageSpec 逆向解析为 ApplicationSpec"""
        use_cases = []
        ports = []

        for sub_pkg in package_spec.sub_packages:
            if sub_pkg.name == "use_cases":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        use_cases.append(UseCaseSpec.from_module_spec(mod))
            elif sub_pkg.name == "ports":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        ports.append(PortSpec.from_module_spec(mod))

        return cls(use_cases=use_cases, ports=ports)

