from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from dataclasses import field, dataclass
from codegen.python_gen.domain.services.test_generator import TestGenerator


@dataclass
class TestMapper:
    
    __test__ = False

    test_generator: TestGenerator = field(default_factory=TestGenerator)

    def to_package_spec(self, context: BoundedContext) -> PackageSpec:
        application_use_case_tests = []
        for use_case in context.application.use_cases:
            module_spec = self.test_generator.to_test_module_spec(
                context=context, use_case=use_case, aggregate=None
            )
            application_use_case_tests.append(module_spec)
        
        sub_packages = []
        
        if application_use_case_tests:
            application_pkg = PackageSpec.create(
                name="application",
                sub_packages=[
                    PackageSpec.create(name="use_cases", modules=application_use_case_tests)
                ]
            )
            sub_packages.append(application_pkg)

        domain_aggregate_tests = []
        for aggregate in context.domain.aggregates:
            module_spec = self.test_generator.to_test_module_spec(
                context=context, use_case=None, aggregate=aggregate
            )
            domain_aggregate_tests.append(module_spec)
        
        if domain_aggregate_tests:
            domain_pkg = PackageSpec.create(
                name="domain",
                sub_packages=[
                    PackageSpec.create(name="aggregates", modules=domain_aggregate_tests)
                ]
            )
            sub_packages.append(domain_pkg)

        return PackageSpec.create(
            name=context.name.to_snake(),
            sub_packages=sub_packages
        )

