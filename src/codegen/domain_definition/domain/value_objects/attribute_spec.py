from typing import Any
from codegen.domain_definition.domain.value_objects.type_definition import (
    TypeDefinition,
)
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.python_gen.domain.enums import FieldFlavor
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from pydantic import Field


class AttributeSpec(TypeDefinition):
    """Standard specification for a class attribute."""

    name: SnakeString
    description: str | None = Field(default=None)
    default: Any | None = Field(default=None)
    # type, container, optional, custom_type_string 继承自 TypeDefinition

    @classmethod
    def create(cls, name: str, type: str, optional: bool = False) -> "AttributeSpec":
        return cls(
            name=SnakeString(name),
            type=type,
            optional=optional,
            custom_type_string=None,
        )

    def to_variable_spec(self, flavor: FieldFlavor | None = None) -> VariableSpec:
        """将 AttributeSpec 转换为 PythonGen VariableSpec"""
        from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec

        # 使用继承的 to_python_annotation() 方法转换类型
        annotation = self.to_python_annotation()

        assignment = None
        if self.default is not None:
            if isinstance(self.default, str):
                # String values: empty string uses from_literal, non-empty uses from_code
                if self.default == "":
                    assignment = AssignmentSpec.from_literal("")
                else:
                    assignment = AssignmentSpec.from_code(self.default)
            else:
                # Handle actual literals (bool, int, float, None, etc.)
                assignment = AssignmentSpec.from_literal(self.default)

            # 如果指定了 flavor，需要包装在 Field/field 中
            if flavor:
                func_name = "Field" if flavor == FieldFlavor.PYDANTIC else "field"
                assignment = AssignmentSpec.from_call(
                    func_name=func_name,
                    kwargs={"default": assignment}
                )
        elif flavor and self.optional:
            # Create default=Field(default=None) or similar
            func_name = "Field" if flavor == FieldFlavor.PYDANTIC else "field"
            assignment = AssignmentSpec.from_call(
                func_name=func_name,
                kwargs={"default": AssignmentSpec.from_literal(None)}
            )
        elif self.optional:
            if flavor:
                func_name = "Field" if flavor == FieldFlavor.PYDANTIC else "field"
                assignment = AssignmentSpec.from_call(
                    func_name=func_name,
                    kwargs={"default": AssignmentSpec.from_literal(None)}
                )
            else:
                assignment = AssignmentSpec.from_literal(None)

        return VariableSpec.create(
            name=self.name,
            type_spec=annotation,
            assignment=assignment,
        )

    @classmethod
    def from_variable_spec(cls, variable_spec: VariableSpec) -> "AttributeSpec":
        """从 PythonGen VariableSpec 逆向解析为 AttributeSpec"""
        # 使用继承的 from_python_annotation() 类方法
        type_def = TypeDefinition.from_python_annotation(variable_spec.type_spec)

        default_value = None
        is_optional = type_def.optional

        if variable_spec.assignment:
            if variable_spec.assignment.code:
                default_value = variable_spec.assignment.code
            elif variable_spec.assignment.literal:
                default_value = variable_spec.assignment.literal.value

            # Handle Field(default=...) wrapper
            if (
                variable_spec.assignment.flavor
                and variable_spec.assignment.flavor.name == "CALL"
            ):
                call = variable_spec.assignment.call
                if call and call.callee in ("Field", "field"):
                    if "default" in call.kwargs:
                        default_arg = call.kwargs["default"]
                        if default_arg.code:
                            default_value = default_arg.code
                        elif default_arg.literal:
                            default_value = default_arg.literal.value
                        if (
                            default_arg.literal
                            and default_arg.literal.value is None
                        ):
                            is_optional = True
                            default_value = None
                    elif "default_factory" in call.kwargs:
                        is_optional = True
                        default_value = None

        return cls(
            name=variable_spec.name,
            type=type_def.type,
            container=type_def.container,
            optional=is_optional,
            default=default_value,
            custom_type_string=type_def.custom_type_string,
        )
