"""
TestSkeletonMapper: Generates parametrized test skeletons from domain metadata.

Produces two files per component:
- test_{name}.py  — test skeleton (safe to regenerate)
- cases_{name}.py — test case data (never overwritten)
"""

from dataclasses import dataclass
from typing import Iterable

from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.value_object_spec import (
    ValueObjectSpec,
)
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_assignment_spec import (
    ModuleAssignmentSpec,
)
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.enums import FunctionType


# Methods to exclude from test generation
_EXCLUDED_METHODS = frozenset({
    "__new__", "__init__", "__post_init__",
    "__get_pydantic_core_schema__", "__get_validators__",
    "create", "model_post_init",
})


def _is_testable_method(method: MethodSpec) -> bool:
    """Determine if a method should get a test skeleton."""
    name = str(method.name)
    if name in _EXCLUDED_METHODS:
        return False
    if name.startswith("_"):
        return False
    return True


def _cases_var_name(method_name: str) -> str:
    """Generate the TEST_CASES variable name for a method."""
    return f"TEST_CASES_{method_name.upper()}"


def _make_execute_method(uc: UseCaseSpec | None = None) -> MethodSpec:
    """Create a virtual 'execute' MethodSpec for use case test case generation."""
    from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
    from codegen.domain_definition.domain.enums import UseCaseKind
    inputs = []
    if uc:
        if uc.kind == UseCaseKind.COMMAND and uc.command:
            inputs = uc.command.attributes
        elif uc.kind == UseCaseKind.QUERY and uc.query:
            inputs = uc.query.attributes
            
    return MethodSpec(name="execute", inputs=inputs, output=MethodOutput(type="Any"))


@dataclass
class TestSkeletonMapper:
    """Maps domain Specs into test skeleton ModuleSpecs (two files per component)."""

    __test__ = False  # Prevent pytest from collecting this class


    # ------------------------------------------------------------------ #
    #  Cases file: cases_{name}.py  (never overwritten)
    # ------------------------------------------------------------------ #

    def to_cases_module_spec(
        self,
        component_name: str,
        methods: list[MethodSpec],
        component_type: str = "behavior",
        src_module: str | None = None,
        class_name: str | None = None,
    ) -> ModuleSpec:
        """Generate the cases_*.py module with explicitly typed case structures."""
        testable = [m for m in methods if _is_testable_method(m)]
        if not testable:
            return ModuleSpec.create(name=f"cases_{component_name}")

        imports = [
            ImportFromSpec.create("typing", ["Any", "Callable", "NamedTuple", "TypedDict"])
        ]

        extra_code = [
            RawCodeSpec.create(
                "# 测试用例数据文件 - 此文件不会被代码生成覆盖\n"
                "# 开发者在此填充测试用例\n"
            )
        ]
        
        assignments = []

        if component_type == "behavior":
            if src_module and class_name:
                imports.append(ImportFromSpec.create(src_module, [class_name]))

            for method in testable:
                var_name = _cases_var_name(str(method.name))
                method_pascal = self._to_pascal(str(method.name))
                
                # 生成 Case NamedTuple
                case_tuple_name = f"{method_pascal}Case"
                
                fields = []
                if class_name:
                    fields.append(f"    instance: {class_name}")
                else:
                    fields.append(f"    instance: Any")
                    
                for attr in method.inputs:
                    fields.append(f"    {attr.name}: {attr.custom_type_string or attr.type}")
                    
                fields.append("    expected: Any")
                
                case_code = f"class {case_tuple_name}(NamedTuple):\n" + "\n".join(fields) + "\n"
                extra_code.append(RawCodeSpec.create(case_code))
                
                assignments.append(
                    ModuleAssignmentSpec.create(
                        name=var_name,
                        value="[]",
                        type_annotation=f"list[{case_tuple_name}]",
                    )
                )

        else:
            # Component type is service, use_case, infrastructure
            # We generate a strict NamedTuple for each method's test cases
            for method in testable:
                var_name = _cases_var_name(str(method.name))
                method_pascal = self._to_pascal(str(method.name))
                
                case_tuple_name = f"{method_pascal}Case"
                
                fields = ["    mocks_setup: Callable"]
                for attr in method.inputs:
                    fields.append(f"    {attr.name}: {attr.custom_type_string or attr.type}")
                fields.append("    expected: Any")
                
                case_code = f"class {case_tuple_name}(NamedTuple):\n" + "\n".join(fields) + "\n"
                extra_code.append(RawCodeSpec.create(case_code))
                
                assignments.append(
                    ModuleAssignmentSpec.create(
                        name=var_name,
                        value="[]",
                        type_annotation=f"list[{case_tuple_name}]",
                    )
                )

        return ModuleSpec.create(
            name=f"cases_{component_name}",
            extra_code=extra_code,
            imports=imports,
            assignments=assignments,
        )

    # ------------------------------------------------------------------ #
    #  Test file: test_{name}.py  (can be regenerated)
    # ------------------------------------------------------------------ #

    def to_service_test_module_spec(
        self,
        service: ServiceSpec,
        context_name: str,
        project_name: str,
    ) -> ModuleSpec:
        """Generate the test_*.py skeleton for a domain service."""
        service_snake = str(service.name).lower()
        # Convert PascalCase to snake_case properly
        import re
        service_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', str(service.name)).lower()

        testable = [m for m in service.operations if _is_testable_method(m)]
        if not testable:
            return ModuleSpec.create(name=f"test_{service_snake}")

        cases_var_names = [_cases_var_name(str(m.name)) for m in testable]
        imports = [
            ImportFromSpec.create("__root__", ["pytest"]),
            ImportFromSpec.create("unittest.mock", ["MagicMock"]),
            ImportFromSpec.create(f"cases_{service_snake}", cases_var_names, level=1),
        ]

        # Build the import path for the service under test
        src_module = (
            f"{project_name}.{context_name}.domain.services.{service_snake}"
        )

        # Dependency mock fixtures
        dep_fixtures: list[FunctionSpec] = []
        dep_names = []
        for dep in service.dependencies:
            dep_name = self._to_snake(str(dep.name))
            dep_names.append(dep_name)
            
            dep_fixture = FunctionSpec.create(
                name=dep_name,
                return_annotation=TypeAnnotationSpec(name="None"),
                decorators=["pytest.fixture"],
                parameters=[],
                suite="return MagicMock()",
                function_type=FunctionType.INSTANCE_METHOD,
            )
            dep_fixtures.append(dep_fixture)

        # Fixture method: instantiate the service
        kw_args = ", ".join(f"{name}={name}" for name in dep_names)
        fixture_body_lines = [
            f"from {src_module} import {service.name}",
            f"return {service.name}({kw_args})",
        ]
        fixture_body = "\n".join(fixture_body_lines)
        
        fixture_params = [
            VariableSpec.create(name=name, type_spec=None) for name in dep_names
        ]

        fixture_func = FunctionSpec.create(
            name="service",
            return_annotation=TypeAnnotationSpec(name="None"),
            decorators=["pytest.fixture"],
            parameters=fixture_params,
            suite=fixture_body,
            function_type=FunctionType.INSTANCE_METHOD,
        )

        # Test methods
        test_methods = []
        for method in testable:
            var_name = _cases_var_name(str(method.name))
            method_name = str(method.name)

            # For Services, we unroll the NamedTuple into our markers
            param_names = ["mocks_setup"] + [attr.name for attr in method.inputs] + ["expected"]
            param_str = ", ".join(param_names)

            kwargs = ", ".join(f"{attr.name}={attr.name}" for attr in method.inputs)
            suite_lines = [
                f"mocks_setup({', '.join(dep_names)})" if dep_names else "mocks_setup()",
                f"result = service.{method_name}({kwargs})",
                "if callable(expected):",
                "    expected(service)",
                "else:",
                "    assert result == expected",
            ]
            
            test_params = [
                VariableSpec.create(name="service", type_spec=None),
            ]
            test_params.extend([
                VariableSpec.create(name=name, type_spec=None) for name in dep_names
            ])
            for p in param_names:
                test_params.append(VariableSpec.create(name=p, type_spec=None))

            test_func = FunctionSpec.create(
                name=f"test_{method_name}",
                return_annotation=TypeAnnotationSpec(name="None"),
                decorators=[
                    f'pytest.mark.parametrize("{param_str}", {var_name})'
                ],
                parameters=test_params,
                suite="\n".join(suite_lines),
                function_type=FunctionType.INSTANCE_METHOD,
            )
            test_methods.append(test_func)

        test_class = ClassSpec.create(
            name=f"Test{service.name}",
            methods=dep_fixtures + [fixture_func] + test_methods,
        )

        return ModuleSpec.create(
            name=f"test_{service_snake}",
            imports=imports,
            classes=[test_class],
        )

    def to_behavior_test_module_spec(
        self,
        name: str,
        behaviors: list[MethodSpec],
        context_name: str,
        project_name: str,
        component_type: str,
    ) -> ModuleSpec:
        """Generate the test_*.py skeleton for VO/Aggregate/Entity behaviors."""
        import re
        component_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

        testable = [m for m in behaviors if _is_testable_method(m)]
        if not testable:
            return ModuleSpec.create(name=f"test_{component_snake}")

        # 具名导入每个 testable method 对应的 TEST_CASES 变量
        cases_var_names = [_cases_var_name(str(m.name)) for m in testable]
        imports = [
            ImportFromSpec.create("__root__", ["pytest"]),
            ImportFromSpec.create(f"cases_{component_snake}", cases_var_names, level=1),
        ]

        src_module = (
            f"{project_name}.{context_name}.domain.{component_type}.{component_snake}"
        )

        test_methods = []
        for method in testable:
            var_name = _cases_var_name(str(method.name))
            method_name = str(method.name)

            param_names = ["instance"] + [attr.name for attr in method.inputs] + ["expected"]
            param_str = ", ".join(param_names)

            kwargs = ", ".join(f"{attr.name}={attr.name}" for attr in method.inputs)
            suite_lines = [
                f"actual = instance.{method_name}({kwargs})",
                "if callable(expected):",
                "    expected(instance)  # 验证对象状态而非返回值",
                "else:",
                "    assert actual == expected",
            ]

            test_params = []
            for p in param_names:
                test_params.append(VariableSpec.create(name=p, type_spec=None))

            test_func = FunctionSpec.create(
                name=f"test_{method_name}",
                return_annotation=TypeAnnotationSpec(name="None"),
                decorators=[
                    f'pytest.mark.parametrize("{param_str}", {var_name})'
                ],
                parameters=test_params,
                suite="\n".join(suite_lines),
                function_type=FunctionType.INSTANCE_METHOD,
            )
            test_methods.append(test_func)

        test_class = ClassSpec.create(
            name=f"Test{name}",
            methods=test_methods,
        )

        return ModuleSpec.create(
            name=f"test_{component_snake}",
            imports=imports,
            classes=[test_class],
        )

    # ------------------------------------------------------------------ #
    #  Use Case test module: test_{name}.py
    # ------------------------------------------------------------------ #

    def to_use_case_test_module_spec(
        self,
        use_case: UseCaseSpec,
        context_name: str,
        project_name: str,
    ) -> ModuleSpec:
        """Generate the test_*.py skeleton for an application use case."""
        uc_snake = self._to_snake(str(use_case.name))
        execute_var = _cases_var_name("execute")

        imports = [
            ImportFromSpec.create("__root__", ["pytest"]),
            ImportFromSpec.create("unittest.mock", ["MagicMock", "AsyncMock"]),
            ImportFromSpec.create(f"cases_{uc_snake}", [execute_var], level=1),
        ]

        src_module = (
            f"{project_name}.{context_name}.application.use_cases.{uc_snake}"
        )

        # Dependency mock fixtures
        dep_fixtures: list[FunctionSpec] = []
        dep_names = []
        for dep in use_case.dependencies:
            dep_name = self._to_snake(str(dep.name))
            dep_names.append(dep_name)
            
            dep_fixture = FunctionSpec.create(
                name=dep_name,
                return_annotation=TypeAnnotationSpec(name="None"),
                decorators=["pytest.fixture"],
                parameters=[],
                suite="return MagicMock()",
                function_type=FunctionType.INSTANCE_METHOD,
            )
            dep_fixtures.append(dep_fixture)

        # Fixture：实例化 use case
        kw_args = ", ".join(f"{name}={name}" for name in dep_names)
        fixture_body = (
            f"from {src_module} import {use_case.name}\n"
            f"return {use_case.name}({kw_args})"
        )
        
        fixture_params = [
            VariableSpec.create(name=name, type_spec=None) for name in dep_names
        ]
        
        fixture_func = FunctionSpec.create(
            name="use_case",
            return_annotation=TypeAnnotationSpec(name="None"),
            decorators=["pytest.fixture"],
            parameters=fixture_params,
            suite=fixture_body,
            function_type=FunctionType.INSTANCE_METHOD,
        )

        # test_execute 方法
        execute_method = _make_execute_method(use_case)
        param_names = ["mocks_setup"] + [attr.name for attr in execute_method.inputs] + ["expected"]
        param_str = ", ".join(param_names)

        kwargs = ", ".join(f"{attr.name}={attr.name}" for attr in execute_method.inputs)
        
        suite_lines = [
            f"mocks_setup({', '.join(dep_names)})" if dep_names else "mocks_setup()",
            f"result = use_case.execute({kwargs})",
            "assert result == expected",
        ]
        
        test_params = [
            VariableSpec.create(name="use_case", type_spec=None),
        ]
        test_params.extend([
            VariableSpec.create(name=name, type_spec=None) for name in dep_names
        ])
        for p in param_names:
            test_params.append(VariableSpec.create(name=p, type_spec=None))

        test_execute = FunctionSpec.create(
            name="test_execute",
            return_annotation=TypeAnnotationSpec(name="None"),
            decorators=[
                f'pytest.mark.parametrize("{param_str}", {execute_var})'
            ],
            parameters=test_params,
            suite="\n".join(suite_lines),
            function_type=FunctionType.INSTANCE_METHOD,
        )

        test_class = ClassSpec.create(
            name=f"Test{use_case.name}",
            methods=dep_fixtures + [fixture_func, test_execute],
        )

        return ModuleSpec.create(
            name=f"test_{uc_snake}",
            imports=imports,
            classes=[test_class],
        )

    # ------------------------------------------------------------------ #
    #  Infrastructure Implementation test module: test_{name}.py
    # ------------------------------------------------------------------ #

    def to_infrastructure_test_module_spec(
        self,
        impl: ImplementationSpec,
        context: BoundedContext,
        project_name: str,
    ) -> ModuleSpec:
        """Generate the test_*.py skeleton for an infrastructure implementation."""
        impl_snake = self._to_snake(str(impl.name))
        
        try:
            port_spec = context.get_port_spec(str(impl.implements))
            testable = [m for m in port_spec.get_final_operations() if _is_testable_method(m)]
        except ValueError:
            # If the port isn't found, we can't generate specific tests for it
            testable = []

        if not testable:
            return ModuleSpec.create(name=f"test_{impl_snake}")

        context_snake = self._to_snake(str(context.name))
        cases_var_names = [_cases_var_name(str(m.name)) for m in testable]
        
        imports = [
            ImportFromSpec.create("__root__", ["pytest"]),
            ImportFromSpec.create("unittest.mock", ["MagicMock"]),
            ImportFromSpec.create(f"cases_{impl_snake}", cases_var_names, level=1),
        ]

        src_module = (
            f"{project_name}.{context_snake}.infrastructure.{impl_snake}"
        )

        # Dependency mock fixtures (Infrastructure implementations often lack explicit deps in schema, 
        # but if they have them via attributes, we mock them)
        dep_fixtures: list[FunctionSpec] = []
        dep_names = []
        for attr in impl.attributes:
            dep_name = self._to_snake(str(attr.name))
            dep_names.append(dep_name)
            
            dep_fixture = FunctionSpec.create(
                name=dep_name,
                return_annotation=TypeAnnotationSpec(name="None"),
                decorators=["pytest.fixture"],
                parameters=[],
                suite="return MagicMock()",
                function_type=FunctionType.INSTANCE_METHOD,
            )
            dep_fixtures.append(dep_fixture)

        # Fixture method: instantiate the implementation
        kw_args = ", ".join(f"{name}={name}" for name in dep_names)
        if kw_args:
            fixture_body_lines = [
                f"from {src_module} import {impl.name}",
                f"return {impl.name}({kw_args})",
            ]
        else:
            fixture_body_lines = [
                f"from {src_module} import {impl.name}",
                f"return {impl.name}()",
            ]
        fixture_body = "\n".join(fixture_body_lines)
        
        fixture_params = [
            VariableSpec.create(name=name, type_spec=None) for name in dep_names
        ]

        fixture_func = FunctionSpec.create(
            name=impl_snake,
            return_annotation=TypeAnnotationSpec(name="None"),
            decorators=["pytest.fixture"],
            parameters=fixture_params,
            suite=fixture_body,
            function_type=FunctionType.INSTANCE_METHOD,
        )

        # Test methods
        test_methods = []
        for method in testable:
            var_name = _cases_var_name(str(method.name))
            method_name = str(method.name)

            param_names = ["mocks_setup"] + [attr.name for attr in method.inputs] + ["expected"]
            param_str = ", ".join(param_names)

            kwargs = ", ".join(f"{attr.name}={attr.name}" for attr in method.inputs)
            suite_lines = [
                f"mocks_setup({', '.join(dep_names)})" if dep_names else "mocks_setup()",
                f"result = {impl_snake}.{method_name}({kwargs})",
                "if callable(expected):",
                f"    expected({impl_snake})",
                "else:",
                "    assert result == expected",
            ]
            
            test_params = [
                VariableSpec.create(name=impl_snake, type_spec=None),
            ]
            test_params.extend([
                VariableSpec.create(name=name, type_spec=None) for name in dep_names
            ])
            for p in param_names:
                test_params.append(VariableSpec.create(name=p, type_spec=None))

            test_func = FunctionSpec.create(
                name=f"test_{method_name}",
                return_annotation=TypeAnnotationSpec(name="None"),
                decorators=[
                    f'pytest.mark.parametrize("{param_str}", {var_name})'
                ],
                parameters=test_params,
                suite="\n".join(suite_lines),
                function_type=FunctionType.INSTANCE_METHOD,
            )
            test_methods.append(test_func)

        test_class = ClassSpec.create(
            name=f"Test{impl.name}",
            methods=dep_fixtures + [fixture_func] + test_methods,
        )

        return ModuleSpec.create(
            name=f"test_{impl_snake}",
            imports=imports,
            classes=[test_class],
        )

    # ------------------------------------------------------------------ #
    #  High-level: BoundedContext → test PackageSpec
    # ------------------------------------------------------------------ #

    def to_test_package_spec(
        self,
        context: BoundedContext,
        project_name: str,
    ) -> PackageSpec:
        """Generate the full tests/unit/{context}/ PackageSpec."""
        import re
        context_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', str(context.name)).lower()
        domain = context.domain
        if not domain:
            return PackageSpec.create(name=context_snake)

        # --- domain/services ---
        service_test_modules: list[ModuleSpec] = []
        service_cases_modules: list[ModuleSpec] = []
        for service in (domain.services or []):
            testable_ops = [m for m in service.operations if _is_testable_method(m)]
            if not testable_ops:
                continue
            service_test_modules.append(
                self.to_service_test_module_spec(service, context_snake, project_name)
            )
            service_cases_modules.append(
                self.to_cases_module_spec(
                    self._to_snake(str(service.name)),
                    service.operations,
                    component_type="service",
                )
            )

        services_pkg = PackageSpec.create(
            name="services",
            modules=service_test_modules + service_cases_modules,
        )

        # --- domain/value_objects ---
        vo_test_modules: list[ModuleSpec] = []
        vo_cases_modules: list[ModuleSpec] = []
        for vo in (domain.value_objects or []):
            if not vo.behaviors:
                continue
            testable = [m for m in vo.behaviors if _is_testable_method(m)]
            if not testable:
                continue
            vo_snake = self._to_snake(str(vo.name))
            src_module = f"{project_name}.{context_snake}.domain.value_objects.{vo_snake}"
            
            vo_test_modules.append(
                self.to_behavior_test_module_spec(
                    str(vo.name), vo.behaviors,
                    context_snake, project_name, "value_objects",
                )
            )
            vo_cases_modules.append(
                self.to_cases_module_spec(
                    vo_snake, vo.behaviors, component_type="behavior",
                    src_module=src_module, class_name=str(vo.name)
                )
            )

        value_objects_pkg = PackageSpec.create(
            name="value_objects",
            modules=vo_test_modules + vo_cases_modules,
        )

        # --- domain/aggregates ---
        agg_test_modules: list[ModuleSpec] = []
        agg_cases_modules: list[ModuleSpec] = []
        for agg in (domain.aggregates or []):
            if not agg.behaviors:
                continue
            testable = [m for m in agg.behaviors if _is_testable_method(m)]
            if not testable:
                continue
            agg_snake = self._to_snake(str(agg.name))
            src_module = f"{project_name}.{context_snake}.domain.aggregates.{agg_snake}"

            agg_test_modules.append(
                self.to_behavior_test_module_spec(
                    str(agg.name), agg.behaviors,
                    context_snake, project_name, "aggregates",
                )
            )
            agg_cases_modules.append(
                self.to_cases_module_spec(
                    agg_snake, agg.behaviors, component_type="behavior",
                    src_module=src_module, class_name=str(agg.name)
                )
            )

        aggregates_pkg = PackageSpec.create(
            name="aggregates",
            modules=agg_test_modules + agg_cases_modules,
        )

        # --- domain/entities ---
        entity_test_modules: list[ModuleSpec] = []
        entity_cases_modules: list[ModuleSpec] = []
        for entity in (domain.entities or []):
            if not entity.behaviors:
                continue
            testable = [m for m in entity.behaviors if _is_testable_method(m)]
            if not testable:
                continue
            ent_snake = self._to_snake(str(entity.name))
            src_module = f"{project_name}.{context_snake}.domain.entities.{ent_snake}"

            entity_test_modules.append(
                self.to_behavior_test_module_spec(
                    str(entity.name), entity.behaviors,
                    context_snake, project_name, "entities",
                )
            )
            entity_cases_modules.append(
                self.to_cases_module_spec(
                    ent_snake, entity.behaviors, component_type="behavior",
                    src_module=src_module, class_name=str(entity.name)
                )
            )

        entities_pkg = PackageSpec.create(
            name="entities",
            modules=entity_test_modules + entity_cases_modules,
        )

        domain_pkg = PackageSpec.create(
            name="domain",
            sub_packages=[services_pkg, value_objects_pkg, aggregates_pkg, entities_pkg],
        )

        # --- application/use_cases ---
        uc_test_modules: list[ModuleSpec] = []
        uc_cases_modules: list[ModuleSpec] = []
        application = context.application
        for uc in (application.use_cases if application else []):
            uc_test_modules.append(
                self.to_use_case_test_module_spec(uc, context_snake, project_name)
            )
            uc_cases_modules.append(
                self.to_cases_module_spec(
                    self._to_snake(str(uc.name)),
                    [_make_execute_method(uc)],
                    component_type="use_case",
                )
            )

        use_cases_pkg = PackageSpec.create(
            name="use_cases",
            modules=uc_test_modules + uc_cases_modules,
        )
        application_pkg = PackageSpec.create(
            name="application",
            sub_packages=[use_cases_pkg],
        )

        # --- infrastructure/implementations ---
        infra_test_modules: list[ModuleSpec] = []
        infra_cases_modules: list[ModuleSpec] = []
        infrastructure = context.infrastructure
        for impl in (infrastructure.implementations if infrastructure else []):
            try:
                port_spec = context.get_port_spec(str(impl.implements))
                testable_ops = [m for m in port_spec.get_final_operations() if _is_testable_method(m)]
            except ValueError:
                testable_ops = []

            if not testable_ops:
                continue

            infra_test_modules.append(
                self.to_infrastructure_test_module_spec(impl, context, project_name)
            )
            infra_cases_modules.append(
                self.to_cases_module_spec(
                    self._to_snake(str(impl.name)),
                    testable_ops,
                    component_type="infrastructure",
                )
            )

        infrastructure_pkg = PackageSpec.create(
            name="infrastructure",
            modules=infra_test_modules + infra_cases_modules,
        )

        return PackageSpec.create(
            name=context_snake,
            sub_packages=[domain_pkg, application_pkg, infrastructure_pkg],
        )

    @staticmethod
    def _to_pascal(snake_name: str) -> str:
        return "".join(word.capitalize() for word in snake_name.split("_"))

    @staticmethod
    def _to_snake(pascal_name: str) -> str:
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', pascal_name).lower()
