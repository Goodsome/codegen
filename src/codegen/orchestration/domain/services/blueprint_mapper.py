from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.context_mapper import ContextMapper
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint


@dataclass
class BlueprintMapper:

    context_mapper: ContextMapper = field(default_factory=ContextMapper)

    def to_package_spec(self, blueprint: Blueprint) -> PackageSpec:
        context_packages = [
            self.context_mapper.to_package_spec(c) for c in blueprint.contexts
        ]
        return PackageSpec.create(
            name=blueprint.name.to_snake(), sub_packages=context_packages
        )

    def to_blueprint(self, package_spec: PackageSpec) -> Blueprint:
        contexts = [
            self.context_mapper.to_context(p)
            for p in package_spec.sub_packages
        ]
        return Blueprint.create(
            name=package_spec.name, description="", contexts=contexts, layout=""
        )
