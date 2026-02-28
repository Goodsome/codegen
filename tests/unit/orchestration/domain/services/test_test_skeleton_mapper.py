"""Unit tests for TestSkeletonMapper."""
import pytest
from codegen.orchestration.domain.services.test_skeleton_mapper import (
    TestSkeletonMapper,
)
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.value_object_spec import (
    ValueObjectSpec,
)
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.domain_spec import DomainSpec


@pytest.fixture
def mapper():
    return TestSkeletonMapper()


def _make_method(name: str, inputs: list[str] | None = None) -> MethodSpec:
    """Helper to create a MethodSpec."""
    attrs = [
        AttributeSpec.create(name=n, type="string") for n in (inputs or [])
    ]
    return MethodSpec(
        name=name,
        inputs=attrs,
        output=MethodOutput(type="str"),
    )


def _make_service(
    name: str, operations: list[MethodSpec], deps: list[str] | None = None
) -> ServiceSpec:
    """Helper to create a ServiceSpec."""
    dependencies = [
        AttributeSpec.create(name=d, type="SomeType") for d in (deps or [])
    ]
    return ServiceSpec(
        name=name,
        operations=operations,
        dependencies=dependencies,
    )


# ============================================================
# Cases module generation
# ============================================================


class TestCasesModuleSpec:
    """Tests for to_cases_module_spec."""

    def test_generates_empty_lists_for_each_testable_method(self, mapper):
        methods = [
            _make_method("do_something", ["arg1", "arg2"]),
            _make_method("do_another"),
        ]
        result = mapper.to_cases_module_spec("my_service", methods)

        assert str(result.name) == "cases_my_service"
        assert len(result.assignments) == 2
        assert result.assignments[0].name == "TEST_CASES_DO_SOMETHING"
        assert result.assignments[1].name == "TEST_CASES_DO_ANOTHER"
        assert "list" == result.assignments[0].type_annotation

    def test_excludes_private_methods(self, mapper):
        methods = [
            _make_method("do_something"),
            _make_method("_private_helper"),
        ]
        result = mapper.to_cases_module_spec("my_service", methods)

        assert len(result.assignments) == 1
        assert result.assignments[0].name == "TEST_CASES_DO_SOMETHING"

    def test_excludes_special_methods(self, mapper):
        methods = [
            _make_method("create"),
            _make_method("__new__"),
            _make_method("__init__"),
            _make_method("__get_pydantic_core_schema__"),
            _make_method("real_method"),
        ]
        result = mapper.to_cases_module_spec("my_vo", methods)

        assert len(result.assignments) == 1
        assert result.assignments[0].name == "TEST_CASES_REAL_METHOD"

    def test_empty_methods_produces_empty_module(self, mapper):
        result = mapper.to_cases_module_spec("empty_thing", [])
        assert len(result.assignments) == 0

    def test_hint_contains_input_names(self, mapper):
        methods = [_make_method("convert", ["source", "target"])]
        result = mapper.to_cases_module_spec("converter", methods)

        value = result.assignments[0].value
        assert '"source"' in value
        assert '"target"' in value


# ============================================================
# Service test module generation
# ============================================================


class TestServiceTestModuleSpec:
    """Tests for to_service_test_module_spec."""

    def test_generates_test_class_with_fixture_and_methods(self, mapper):
        service = _make_service(
            "EnumMapper",
            operations=[
                _make_method("to_python_enum_spec", ["meta_enum"]),
                _make_method("to_module_spec", ["enums"]),
            ],
        )
        result = mapper.to_service_test_module_spec(
            service, "orchestration", "my_project"
        )

        assert str(result.name) == "test_enum_mapper"
        assert len(result.classes) == 1

        test_class = result.classes[0]
        assert str(test_class.name) == "TestEnumMapper"
        # fixture + 2 test methods
        assert len(test_class.methods) == 3
        assert str(test_class.methods[0].name) == "service"
        assert str(test_class.methods[1].name) == "test_to_python_enum_spec"
        assert str(test_class.methods[2].name) == "test_to_module_spec"

    def test_skips_private_operations(self, mapper):
        service = _make_service(
            "MyService",
            operations=[
                _make_method("public_op"),
                _make_method("_private_helper"),
            ],
        )
        result = mapper.to_service_test_module_spec(
            service, "sales", "project"
        )

        test_class = result.classes[0]
        # fixture + 1 test method (private skipped)
        assert len(test_class.methods) == 2

    def test_fixture_imports_correct_module(self, mapper):
        service = _make_service(
            "BlueprintMapper",
            operations=[_make_method("to_package_spec", ["blueprint"])],
        )
        result = mapper.to_service_test_module_spec(
            service, "orchestration", "codegen"
        )

        fixture = result.classes[0].methods[0]
        assert "codegen.orchestration.domain.services.blueprint_mapper" in fixture.suite
        assert "BlueprintMapper" in fixture.suite

    def test_has_pytest_import(self, mapper):
        service = _make_service(
            "Simple", operations=[_make_method("go")]
        )
        result = mapper.to_service_test_module_spec(
            service, "shared", "proj"
        )

        import_modules = [imp.module for imp in result.imports]
        assert "__root__" in import_modules
        pytest_import = [i for i in result.imports if i.module == "__root__"]
        assert any(i.has_name("pytest") for i in pytest_import)

    def test_has_cases_import(self, mapper):
        service = _make_service(
            "Simple", operations=[_make_method("go")]
        )
        result = mapper.to_service_test_module_spec(
            service, "shared", "proj"
        )

        # Cases import should be a relative import (level=1)
        cases_imports = [i for i in result.imports if i.level == 1]
        assert len(cases_imports) == 1
        assert "cases_simple" in cases_imports[0].module

    def test_empty_operations_produces_empty_test_class(self, mapper):
        service = _make_service("NoOps", operations=[])
        result = mapper.to_service_test_module_spec(
            service, "ctx", "proj"
        )
        assert len(result.classes) == 0


# ============================================================
# Behavior test module generation
# ============================================================


class TestBehaviorTestModuleSpec:
    """Tests for to_behavior_test_module_spec."""

    def test_generates_test_for_value_object(self, mapper):
        behaviors = [
            _make_method("render"),
            _make_method("merge", ["other"]),
            _make_method("create"),  # should be excluded
        ]
        result = mapper.to_behavior_test_module_spec(
            "TypeAnnotationSpec", behaviors,
            "python_gen", "codegen", "value_objects",
        )

        assert str(result.name) == "test_type_annotation_spec"
        test_class = result.classes[0]
        assert str(test_class.name) == "TestTypeAnnotationSpec"
        # fixture + 2 testable methods (create excluded)
        assert len(test_class.methods) == 3

    def test_fixture_points_to_correct_import(self, mapper):
        result = mapper.to_behavior_test_module_spec(
            "Address", [_make_method("validate")],
            "sales", "my_project", "value_objects",
        )

        fixture = result.classes[0].methods[0]
        assert "my_project.sales.domain.value_objects.address" in fixture.suite


# ============================================================
# Full context package generation
# ============================================================


class TestPackageSpec:
    """Tests for to_test_package_spec."""

    def test_generates_full_context_structure(self, mapper):
        context = BoundedContext.create(
            name="Sales",
            domain=DomainSpec(
                services=[
                    _make_service("OrderService", [
                        _make_method("create_order", ["amount"]),
                    ]),
                ],
                value_objects=[
                    ValueObjectSpec(
                        name="Money",
                        behaviors=[_make_method("add", ["other"])],
                    ),
                ],
                aggregates=[
                    AggregateSpec(
                        name="Order",
                        behaviors=[_make_method("add_item", ["item"])],
                    ),
                ],
                entities=[
                    EntitySpec(
                        name="Product",
                        behaviors=[_make_method("update_price", ["price"])],
                    ),
                ],
            ),
        )

        result = mapper.to_test_package_spec(context, "my_project")

        assert str(result.name) == "sales"
        # domain sub-package
        domain_pkg = result.sub_packages[0]
        assert str(domain_pkg.name) == "domain"
        # 4 sub-packages: services, value_objects, aggregates, entities
        assert len(domain_pkg.sub_packages) == 4

        services_pkg = domain_pkg.sub_packages[0]
        assert str(services_pkg.name) == "services"
        # test + cases for OrderService (+ __init__)
        module_names = {str(m.name) for m in services_pkg.modules}
        assert "test_order_service" in module_names
        assert "cases_order_service" in module_names

    def test_skips_context_without_domain(self, mapper):
        context = BoundedContext.create(name="Empty")
        result = mapper.to_test_package_spec(context, "proj")
        assert result.is_empty()

    def test_skips_components_without_testable_methods(self, mapper):
        context = BoundedContext.create(
            name="Sales",
            domain=DomainSpec(
                services=[
                    _make_service("InternalService", [
                        _make_method("_private_only"),
                    ]),
                ],
                value_objects=[
                    ValueObjectSpec(
                        name="Simple",
                        # No behaviors
                    ),
                ],
            ),
        )

        result = mapper.to_test_package_spec(context, "proj")
        domain_pkg = result.sub_packages[0]
        services_pkg = domain_pkg.sub_packages[0]
        # No testable operations → only __init__ module
        non_init = [m for m in services_pkg.modules if str(m.name) != "__init__"]
        assert len(non_init) == 0
