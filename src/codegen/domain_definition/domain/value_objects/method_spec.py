import logging
from typing import Literal, Self

from pydantic import Field

from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.rule_spec import RuleSpec
from codegen.domain_definition.domain.value_objects.type_definition import (
    TypeDefinition,
)
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.module_assignment_spec import (
    ModuleAssignmentSpec,
)
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.domain.core import ValueObject


logger = logging.getLogger(__name__)

class MethodSpec(ValueObject):
    """Standard specification for a class method."""

    name: SnakeString
    description: str | None = Field(default=None)
    inputs: list[AttributeSpec] = Field(default_factory=list)
    output: MethodOutput
    rules: list[RuleSpec] = Field(default_factory=list)
    is_async: bool = False

    @classmethod
    def create(
        cls: type[Self], name: str, inputs: list[AttributeSpec], output: MethodOutput
    ) -> Self:
        return cls(name=SnakeString(name), inputs=inputs, output=output)

    def function_type(self) -> FunctionType:
        for attr in self.inputs:
            if attr.name == "cls":
                return FunctionType.CLASS_METHOD
            if attr.name == "self":
                return FunctionType.INSTANCE_METHOD
        return FunctionType.FUNCTION

    def to_function_spec(self: Self) -> FunctionSpec:
        """将 MethodSpec 转换为 PythonGen FunctionSpec"""
        parameters = [attr.to_variable_spec() for attr in self.inputs or []]
        decorators = []
        ft = self.function_type()
        if ft == FunctionType.CLASS_METHOD:
            decorators.append("classmethod")
        elif ft == FunctionType.STATIC_METHOD:
            decorators.append("staticmethod")
        return_annotation = self.output.to_python_annotation()
        return FunctionSpec.create(
            name=self.name,
            parameters=parameters,
            decorators=decorators,
            return_annotation=return_annotation,
            function_type=ft,
            suite="...",
            is_async=self.is_async,
        )

    @classmethod
    def from_function_spec(cls: type[Self], function_spec: FunctionSpec) -> Self:
        """从 PythonGen FunctionSpec 逆向解析为 MethodSpec"""
        inputs: list[AttributeSpec] = []
        for param in function_spec.parameters:
            if (
                function_spec.function_type == FunctionType.INSTANCE_METHOD
                and param.name == "self"
            ):
                self_var_spec = VariableSpec.create(
                    name=param.name,
                    type_spec=TypeAnnotationSpec(name="Self"),
                    assignment=None,
                )
                inputs.append(AttributeSpec.from_variable_spec(self_var_spec))
                continue
            if (
                function_spec.function_type == FunctionType.CLASS_METHOD
                and param.name == "cls"
            ):
                cls_var_spec = VariableSpec.create(
                    name=param.name,
                    type_spec=TypeAnnotationSpec(
                        name="type", args=[TypeAnnotationSpec(name="Self")]
                    ),
                    assignment=None,
                )
                inputs.append(AttributeSpec.from_variable_spec(cls_var_spec))
                continue
            inputs.append(AttributeSpec.from_variable_spec(param))
        type_def = TypeDefinition.from_python_annotation(
            function_spec.return_annotation
        )
        return cls(
            name=function_spec.name,
            description=function_spec.description,
            inputs=inputs,
            output=MethodOutput(
                type=type_def.type,
                container=type_def.container,
                optional=type_def.optional,
                custom_type_string=type_def.custom_type_string,
            ),
            is_async=function_spec.is_async,
        )

    def to_test_module_spec(self: Self) -> ModuleSpec:
        """Generate test module with test functions for each rule."""
        bindings_name = f"{self.name}_bindings"
        functions = [rule.to_test_function_spec(bindings_name) for rule in self.rules]
        return ModuleSpec.create(
            name=f"test_{self.name}",
            functions=functions,
            assignments=[
                ModuleAssignmentSpec(
                    name="_", value=bindings_name, require_types=[bindings_name]
                )
            ],
        )

    def to_bindings_module_spec(self: Self) -> ModuleSpec:
        """Generate bindings module with match-case routing for given/when/then."""
        bindings_name = f"{PascalString(self.name)}Bindings"
        gf = self._get_match_semantic_function("given")
        wf = self._get_match_semantic_function("when")
        tf = self._get_match_semantic_function("then")
        and_f = self._get_dispatch_function("and_")
        but_f = self._get_dispatch_function("but")
        
        af = FunctionSpec.create(
            name="arrange_done",
            return_annotation=TypeAnnotationSpec(name="Self"),
            parameters=[
                VariableSpec.create(
                    name="self",
                    type_spec=TypeAnnotationSpec(name="Self"),
                )
            ],
            function_type=FunctionType.INSTANCE_METHOD,
            suite="""return self""",
        )
        bc = ClassSpec.create(
            name=bindings_name,
            methods=[gf, af, wf, tf, and_f, but_f],
            decorators=["dataclass"],
            attributes=[
                AttributeSpec.create(
                    name="_last_step_type",
                    type="str",
                    optional=True,
                ).to_variable_spec()
            ],
        )
        bf = self._get_bindings_fixture()
        return ModuleSpec.create(
            name=f"bindings_{self.name}",
            classes=[bc],
            functions=[bf],
        )

    def _get_match_semantic_function(self, name: str) -> FunctionSpec:
        return FunctionSpec.create(
            name=name,
            return_annotation=TypeAnnotationSpec(name="Self"),
            parameters=[
                VariableSpec.create(
                    name="self",
                    type_spec=TypeAnnotationSpec(name="Self"),
                ),
                VariableSpec.create(
                    name="semantic_text",
                    type_spec=TypeAnnotationSpec(name="str"),
                ),
            ],
            function_type=FunctionType.INSTANCE_METHOD,
            suite=f"""
self._last_step_type = "{name}"

match semantic_text:
    case _:
        raise NotImplementedError(f"未实现的 {name} 语义: {{semantic_text}}")
return self""",
        )
    
    def _get_dispatch_function(self, name: Literal["and_", "but"]) -> FunctionSpec:
        f_suite = """
if not self._last_step_type:
    raise RuntimeError("Cannot use 'and/but' before any Given/When/Then step.")
if self._last_step_type == "given":
    return self.given(semantic_text)
if self._last_step_type == "when":
    return self.when(semantic_text)
if self._last_step_type == "then":
    return self.then(semantic_text)
raise RuntimeError(f"Unexpected last step type: {self._last_step_type}")
"""

        return FunctionSpec.create(
            name=name,
            return_annotation=TypeAnnotationSpec(name="Self"),
            parameters=[
                VariableSpec.create(
                    name="self",
                    type_spec=TypeAnnotationSpec(name="Self"),
                ),
                VariableSpec.create(
                    name="semantic_text",
                    type_spec=TypeAnnotationSpec(name="str"),
                ),
            ],
            function_type=FunctionType.INSTANCE_METHOD,
            suite=f_suite,
        )

    def _get_bindings_fixture(self) -> FunctionSpec:
        bindings_name = f"{PascalString(self.name)}Bindings"
        return FunctionSpec.create(
            name=bindings_name,
            return_annotation=TypeAnnotationSpec(name=bindings_name),
            decorators=["pytest.fixture"],
            function_type=FunctionType.FUNCTION,
            suite=f"""return {bindings_name}()""",
        )

    def load_test_module(self: Self, module: ModuleSpec) -> Self:
        """Load test cases from module into method rules. Returns self for chaining."""
        for function in module.functions:
            # Skip fixtures and special functions
            if function.name.startswith("test_"):
                rule = RuleSpec.from_test_function(function)
                self.rules.append(rule)

        return self
