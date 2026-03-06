from dataclasses import dataclass, field
from codegen.orchestration.domain.value_objects.build_result import BuildResult
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprint,
    LoadBlueprintCommand,
)
from codegen.orchestration.domain.services.blueprint_mapper import BlueprintMapper
from codegen.orchestration.domain.services.test_skeleton_mapper import (
    TestSkeletonMapper,
)
from codegen.python_gen.application.use_cases.generate_package import (
    GeneratePackage,
    GeneratePackageCommand,
)
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from typing import Union


@dataclass(frozen=True)
class GenerateProjectCommand:

    overwrite: bool
    node: str | None
    root_path: str = ""
    generate_tests: bool = False


@dataclass(frozen=True)
class GenerateProjectResult:

    result: BuildResult


@dataclass
class GenerateProject:

    loader: LoadBlueprint
    generator: GeneratePackage
    test_generator: GeneratePackage  # writes to project root (for tests/)
    mapper: BlueprintMapper = field(default_factory=BlueprintMapper)
    test_mapper: TestSkeletonMapper = field(default_factory=TestSkeletonMapper)

    def execute(self, cmd: GenerateProjectCommand) -> GenerateProjectResult:

        load_result = self.loader.execute(LoadBlueprintCommand(node=cmd.node))
        package_spec = self.mapper.to_package_spec(load_result.blueprint)
        gen_result = self.generator.execute(
            GeneratePackageCommand(
                package_spec=package_spec,
                node=cmd.node,
                overwrite=cmd.overwrite,
                root_path=cmd.root_path,
            )
        )

        if cmd.generate_tests:
            self._generate_test_skeletons(load_result.blueprint)

        return GenerateProjectResult(result=gen_result.result)

    def _generate_test_skeletons(self, blueprint) -> None:
        """Generate test skeleton files for all contexts."""
        import re
        project_name = re.sub(
            r'(?<!^)(?=[A-Z])', '_', str(blueprint.name)
        ).lower()

        test_context_packages: list[PackageSpec] = []
        for context in blueprint.contexts:
            test_pkg = self.test_mapper.to_test_package_spec(
                context, project_name
            )
            if not test_pkg.is_empty():
                test_context_packages.append(test_pkg)

        if not test_context_packages:
            return

        # Split into cases files and test files for different overwrite policies
        cases_packages: list[PackageSpec] = []
        test_packages: list[PackageSpec] = []
        for ctx_pkg in test_context_packages:
            cases_packages.append(self._filter_package(ctx_pkg, prefix="cases_"))
            test_packages.append(self._filter_package(ctx_pkg, prefix="test_"))

        # Pass 1: cases files (merge into existing file — preserves hand-edited data,
        #         while adding newly introduced TEST_CASES variables for new behaviors)
        # NOTE: overwrite=True is intentional here. generate_package already merges the
        #       new ModuleSpec with the existing file on disk, so user-edited test data
        #       is preserved while new TEST_CASES_XXX variables are appended.
        if cases_packages:
            unit_pkg = PackageSpec.create(
                name="unit", sub_packages=cases_packages,
            )
            cases_root = PackageSpec.create(
                name="tests", sub_packages=[unit_pkg],
            )
            self.test_generator.execute(
                GeneratePackageCommand(
                    package_spec=cases_root,
                    node=None,
                    overwrite=True,
                )
            )

        # Pass 2: test skeletons (always overwrite — safe to regenerate)
        if test_packages:
            unit_pkg = PackageSpec.create(
                name="unit", sub_packages=test_packages,
            )
            test_root = PackageSpec.create(
                name="tests", sub_packages=[unit_pkg],
            )
            self.test_generator.execute(
                GeneratePackageCommand(
                    package_spec=test_root,
                    node=None,
                    overwrite=True,
                )
            )

    def _filter_package(self, pkg: PackageSpec, prefix: str) -> PackageSpec:
        """Recursively filter a PackageSpec keeping only modules matching prefix."""
        filtered_modules = [
            m for m in (pkg.modules or [])
            if str(m.name).startswith(prefix) or str(m.name) == "__init__"
        ]
        filtered_sub = [
            self._filter_package(sub, prefix)
            for sub in (pkg.sub_packages or [])
        ]
        return PackageSpec.create(
            name=str(pkg.name),
            modules=filtered_modules,
            sub_packages=filtered_sub,
        )
