from codegen.orchestration.domain.services.implementation_mapper import (
    ImplementationMapper,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    MetaInfrastructure,
)
from dataclasses import dataclass, field
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.domain_definition.domain.value_objects.meta_implementation import (
    MetaImplementation,
)


@dataclass
class InfrastructureMapper:

    implementation_mapper: ImplementationMapper = field(default_factory=ImplementationMapper)

    def to_package_spec(self, infrastructure: MetaInfrastructure) -> PackageSpec:
        acl_modules = [
            self.implementation_mapper.to_module_spec(impl)
            for impl in infrastructure.acl
        ]
        # 对于 adapters，由于 MetaInfrastructureAdapter 结构类似 MetaImplementation，我们可以复用逻辑
        adapter_modules = []
        for adapter in infrastructure.adapters:
            impl = MetaImplementation(
                name=adapter.name,
                implements=adapter.implements,
                description=adapter.description,
                attributes=[],  # Config 转换逻辑视需求而定，这里简化
            )
            adapter_modules.append(self.implementation_mapper.to_module_spec(impl))

        acl_pkg = PackageSpec.create(name="acl", modules=acl_modules)
        adapters_pkg = PackageSpec.create(name="adapters", modules=adapter_modules)

        return PackageSpec.create(
            name="infrastructure", sub_packages=[acl_pkg, adapters_pkg]
        )

    def to_infrastructure(self, package_spec: PackageSpec) -> MetaInfrastructure:
        acl = []
        # adapters 转换略
        for sub_pkg in package_spec.sub_packages:
            if sub_pkg.name == "acl":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        acl.append(self.implementation_mapper.to_implementation(mod))

        return MetaInfrastructure(acl=acl)
