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
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.application_spec import ApplicationSpec
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
        assert "list[DoSomethingCase]" == result.assignments[0].type_annotation

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
        assert "[]" == value
        extra_src = "\n".join(code.code for code in result.extra_code)
        assert "class ConvertCase(NamedTuple):" in extra_src
        assert "source: string" in extra_src
        assert "target: string" in extra_src


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

        # Cases import 应为具名导入（不是 import *）
        cases_imports = [i for i in result.imports if i.level == 1]
        assert len(cases_imports) == 1
        assert "cases_simple" in cases_imports[0].module
        # 应显式导入具体的 TEST_CASES 变量名
        assert cases_imports[0].has_name("TEST_CASES_GO")
        assert not cases_imports[0].has_name("*"), "cases import 不应该使用 import *"

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
        # 2 testable methods (create excluded, fixture removed in V2)
        assert len(test_class.methods) == 2

    def test_cases_import_is_named_not_wildcard(self, mapper):
        """cases import 应为具名导入，而非 import *，且包含所有 testable method。"""
        behaviors = [
            _make_method("add_item", ["product_id"]),
            _make_method("remove_item", ["product_id"]),
        ]
        result = mapper.to_behavior_test_module_spec(
            "Order", behaviors,
            "sales", "my_project", "aggregates",
        )

        cases_imports = [i for i in result.imports if i.level == 1]
        assert len(cases_imports) == 1
        assert not cases_imports[0].has_name("*"), "cases import 不应使用 import *"
        assert cases_imports[0].has_name("TEST_CASES_ADD_ITEM")
        assert cases_imports[0].has_name("TEST_CASES_REMOVE_ITEM")

    def test_imports_domain_model_in_cases(self, mapper):
        result = mapper.to_cases_module_spec(
            "address", [_make_method("validate")], 
            component_type="behavior",
            src_module="my_project.sales.domain.value_objects.address",
            class_name="Address",
        )
        assert "my_project.sales.domain.value_objects.address" == result.imports[1].module
        assert result.imports[1].has_name("Address")


# ============================================================
# Use Case test module generation
# ============================================================


class TestUseCaseTestModuleSpec:
    """Tests for to_use_case_test_module_spec."""

    def test_generates_test_class_with_execute_method(self, mapper):
        uc = UseCaseSpec.create(
            name="CreateOrder",
            kind="command",
        )
        result = mapper.to_use_case_test_module_spec(uc, "sales", "my_project")

        assert str(result.name) == "test_create_order"
        assert len(result.classes) == 1
        cls = result.classes[0]
        assert str(cls.name) == "TestCreateOrder"
        # fixture + test_execute
        assert len(cls.methods) == 2
        assert str(cls.methods[0].name) == "use_case"
        assert str(cls.methods[1].name) == "test_execute"

    def test_fixture_imports_correct_use_case_module(self, mapper):
        uc = UseCaseSpec.create(name="PlaceOrder", kind="command")
        result = mapper.to_use_case_test_module_spec(uc, "sales", "my_project")

        fixture = result.classes[0].methods[0]
        assert "my_project.sales.application.use_cases.place_order" in fixture.suite
        assert "PlaceOrder" in fixture.suite

    def test_cases_import_contains_test_cases_execute(self, mapper):
        uc = UseCaseSpec.create(name="CreateOrder", kind="command")
        result = mapper.to_use_case_test_module_spec(uc, "sales", "my_project")

        cases_imports = [i for i in result.imports if i.level == 1]
        assert len(cases_imports) == 1
        assert "cases_create_order" in cases_imports[0].module
        assert cases_imports[0].has_name("TEST_CASES_EXECUTE")
        assert not cases_imports[0].has_name("*"), "cases import 不应使用 import *"

    def test_cases_module_spec_has_execute_assignment(self, mapper):
        uc = UseCaseSpec.create(name="CreateOrder", kind="command")
        # cases module 包含 TEST_CASES_EXECUTE 变量
        from codegen.orchestration.domain.services.test_skeleton_mapper import _make_execute_method
        cases_mod = mapper.to_cases_module_spec(
            "create_order", [_make_execute_method()]
        )
        assert len(cases_mod.assignments) == 1
        assert cases_mod.assignments[0].name == "TEST_CASES_EXECUTE"




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
        # 应包含 domain + application 两个子包
        pkg_names = {str(p.name) for p in result.sub_packages}
        assert "domain" in pkg_names
        assert "application" in pkg_names

        domain_pkg = next(p for p in result.sub_packages if str(p.name) == "domain")
        # 4 sub-packages: services, value_objects, aggregates, entities
        assert len(domain_pkg.sub_packages) == 4

        services_pkg = next(p for p in domain_pkg.sub_packages if str(p.name) == "services")
        # test + cases for OrderService (+ __init__)
        module_names = {str(m.name) for m in services_pkg.modules}
        assert "test_order_service" in module_names
        assert "cases_order_service" in module_names

    def test_generates_use_cases_under_application(self, mapper):
        """use_case 应在 application/use_cases/ 目录下生成测试骨架。"""
        context = BoundedContext.create(
            name="Sales",
            application=ApplicationSpec(
                use_cases=[
                    UseCaseSpec.create(name="CreateOrder", kind="command"),
                    UseCaseSpec.create(name="CancelOrder", kind="command"),
                ]
            ),
        )
        result = mapper.to_test_package_spec(context, "my_project")

        pkg_names = {str(p.name) for p in result.sub_packages}
        assert "application" in pkg_names

        app_pkg = next(p for p in result.sub_packages if str(p.name) == "application")
        uc_pkg = next(p for p in app_pkg.sub_packages if str(p.name) == "use_cases")
        module_names = {str(m.name) for m in uc_pkg.modules}
        assert "test_create_order" in module_names
        assert "cases_create_order" in module_names
        assert "test_cancel_order" in module_names
        assert "cases_cancel_order" in module_names

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
        domain_pkg = next(p for p in result.sub_packages if str(p.name) == "domain")
        services_pkg = next(p for p in domain_pkg.sub_packages if str(p.name) == "services")
        # No testable operations → only __init__ module
        non_init = [m for m in services_pkg.modules if str(m.name) != "__init__"]
        assert len(non_init) == 0
