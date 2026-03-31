from codegen.domain_definition.domain.value_objects.method_output import MethodOutput
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)
from codegen.python_gen.domain.enums import FunctionType
from codegen.domain_definition.domain.value_objects.type_definition import (
    TypeDefinition,
)
from pydantic import Field
from codegen.domain_definition.domain.value_objects.rule_spec import RuleSpec
from typing import Self, Union


class MethodSpec(ValueObject):
    """Standard specification for a class method."""

    name: SnakeString
    description: str | None = Field(default=None)
    inputs: list[AttributeSpec] | None = Field(default=None)
    output: MethodOutput
    rules: list[RuleSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls: type[Self], name: str, inputs: list[AttributeSpec], output: MethodOutput
    ) -> Self:
        return cls(name=SnakeString(name), inputs=inputs, output=output)

    def to_function_spec(
        self: Self, type: FunctionType, class_name: str | None = None
    ) -> FunctionSpec:
        """将 MethodSpec 转换为 PythonGen FunctionSpec"""
        parameters = [attr.to_variable_spec() for attr in self.inputs or []]
        decorators = []
        if type == FunctionType.CLASS_METHOD:
            decorators.append("classmethod")
        elif type == FunctionType.STATIC_METHOD:
            decorators.append("staticmethod")
        function_name = self.name
        return_type = self.output.custom_type_string or self.output.type
        if class_name and return_type == class_name:
            return_annotation = TypeAnnotationSpec(name="Self")
            if self.output.optional:
                return_annotation = TypeAnnotationSpec(
                    name="Union",
                    args=[
                        TypeAnnotationSpec(name="Self"),
                        TypeAnnotationSpec(name="None"),
                    ],
                )
        else:
            return_annotation = self.output.to_python_annotation()
        return FunctionSpec.create(
            name=function_name,
            parameters=parameters,
            decorators=decorators,
            return_annotation=return_annotation,
            function_type=type,
            suite="...",
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
        )
