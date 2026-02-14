from codegen.domain_definition.domain.value_objects.bounded_context import (
    BoundedContext,
)
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from dataclasses import dataclass


@dataclass
class TestGenerator:
    """Generator for automated test skeletons."""

    def to_test_module_spec(
        self,
        context: BoundedContext,
        use_case: UseCaseSpec | None,
        aggregate: AggregateSpec | None,
    ) -> ModuleSpec:
        if use_case:
            return self._generate_use_case_test(context, use_case)
        if aggregate:
            return self._generate_aggregate_test(context, aggregate)
        raise ValueError("Either use_case or aggregate must be provided.")

    def _generate_use_case_test(
        self, context: BoundedContext, use_case: UseCaseSpec
    ) -> ModuleSpec:
        test_module_name = f"test_{use_case.name.to_snake()}"

        # 1. Imports
        imports = [
            ImportFromSpec.create(module="__root__", names=["pytest"]),
            ImportFromSpec.create(module="typing", names=["Any"]),
        ]

        # 2. Test Function
        params = [
            ParameterSpec.create(
                name="mocker", annotation=TypeAnnotationSpec.parse("Any")
            )
        ]

        # Body
        body_lines = ["# Arrange"]
        # Mock dependencies
        mock_vars = []
        for dep in use_case.dependencies:
            mock_name = f"mock_{dep.name}"
            body_lines.append(f"{mock_name} = mocker.Mock(spec={dep.type})")
            mock_vars.append(f"{dep.name}={mock_name}")

        # Instantiate UseCase
        body_lines.append("")
        body_lines.append(f"use_case = {use_case.name}({', '.join(mock_vars)})")

        # Command/Query
        if use_case.command and use_case.command.name:
            body_lines.append(
                f"command = {use_case.command.name}(...)  # TODO: Fill fields"
            )
            exec_arg = "command"
        elif use_case.query and use_case.query.name:
            body_lines.append(f"query = {use_case.query.name}(...)  # TODO: Fill fields")
            exec_arg = "query"
        else:
            exec_arg = ""

        body_lines.append("")
        body_lines.append("# Act")
        body_lines.append(f"result = use_case.execute({exec_arg})")

        body_lines.append("")
        body_lines.append("# Assert")
        body_lines.append("assert result is not None")

        test_func = FunctionSpec.create(
            name=f"test_{use_case.name.to_snake()}_success",
            return_annotation=TypeAnnotationSpec.parse("None"),
            parameters=params,
            suite="\n".join(body_lines),
        )

        return ModuleSpec.create(
            name=test_module_name,
            functions=[test_func],
            imports=imports,
        )

    def _generate_aggregate_test(
        self, context: BoundedContext, aggregate: AggregateSpec
    ) -> ModuleSpec:
        test_module_name = f"test_{aggregate.name.to_snake()}"

        body_lines = [
            "# Arrange & Act",
            f"aggregate = {aggregate.name}(",
            "    # TODO: Fill attributes",
            ")",
            "",
            "# Assert",
            "assert aggregate is not None",
        ]

        test_func = FunctionSpec.create(
            name=f"test_{aggregate.name.to_snake()}_creation",
            return_annotation=TypeAnnotationSpec.parse("None"),
            suite="\n".join(body_lines),
        )

        return ModuleSpec.create(
            name=test_module_name,
            functions=[test_func],
        )
