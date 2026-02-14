from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from dataclasses import dataclass, field
from codegen.orchestration.domain.services.context_mapper import ContextMapper
from codegen.domain_definition.domain.value_objects.blueprint import Blueprint
from codegen.orchestration.domain.services.test_mapper import TestMapper


@dataclass
class BlueprintMapper:

    context_mapper: ContextMapper = field(default_factory=ContextMapper)
    test_mapper: TestMapper = field(default_factory=TestMapper)

    def to_package_spec(self, blueprint: Blueprint) -> PackageSpec:
        context_packages = [
            self.context_mapper.to_package_spec(c) for c in blueprint.contexts
        ]

        test_sub_packages = []
        for context in blueprint.contexts:
            test_pkg = self.test_mapper.to_package_spec(context)
            if not test_pkg.is_empty():
                test_sub_packages.append(test_pkg)

        if test_sub_packages:
            tests_root = PackageSpec.create(name="tests", sub_packages=test_sub_packages)
            context_packages.append(tests_root)

        return PackageSpec.create(
            name=blueprint.name.to_snake(), sub_packages=context_packages
        )

    def to_blueprint(self, package_spec: PackageSpec) -> Blueprint:
        contexts = [
            self.context_mapper.to_context(p)
            for p in package_spec.sub_packages
            if p.name != "tests"
        ]
        return Blueprint.create(
            name=package_spec.name, description="", contexts=contexts, layout=""
        )
