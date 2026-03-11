from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.context_mapper import ContextMapper
from codegen.orchestration.domain.services.bootstrap_mapper import BootstrapMapper
from codegen.orchestration.domain.services.entrypoint_mapper import EntrypointMapper
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint


@dataclass
class BlueprintMapper:
    context_mapper: ContextMapper = field(default_factory=ContextMapper)
    bootstrap_mapper: BootstrapMapper = field(default_factory=BootstrapMapper)
    entrypoint_mapper: EntrypointMapper = field(default_factory=EntrypointMapper)

    def to_package_spec(self, blueprint: Blueprint) -> PackageSpec:
        project_name = blueprint.name.to_snake()
        context_packages = [
            self.context_mapper.to_package_spec(c, project_name=project_name) for c in blueprint.contexts
        ]

        # Generate bootstrap package if blueprint has bootstrap spec
        if blueprint.bootstrap:
            bootstrap_pkg = self.bootstrap_mapper.to_package_spec(blueprint)
            if bootstrap_pkg:
                context_packages.append(bootstrap_pkg)

        # Generate entrypoints package if any context has interfaces
        has_interfaces = any(
            ctx.interfaces and (ctx.interfaces.cli or ctx.interfaces.mcp or ctx.interfaces.http)
            for ctx in blueprint.contexts
        )
        if has_interfaces:
            entrypoints_pkg = self.entrypoint_mapper.to_package_spec(
                contexts=blueprint.contexts,
                project_name=str(blueprint.name),
            )
            context_packages.append(entrypoints_pkg)

        return PackageSpec.create(
            name=blueprint.name.to_snake(), sub_packages=context_packages
        )

    def to_blueprint(self, package_spec: PackageSpec) -> Blueprint:
        contexts = [
            self.context_mapper.to_context(p) for p in package_spec.sub_packages
        ]
        return Blueprint.create(
            name=package_spec.name, description="", contexts=contexts, layout=""
        )
