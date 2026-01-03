"""
Kind: ValueObject
Name: FunctionSpec
Description: Represents a function in a Python module.
"""

import ast

from codegen.python_gen.domain.enums import FunctionType
from pydantic import Field

from codegen.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import (
    TypeAnnotationSpec,
)


class FunctionSpec(ValueObject):
    """Represents a function in a Python module."""

    name: str
    decorators: list[str] = Field(default_factory=list)
    parameters: list[ParameterSpec] = Field(default_factory=list)
    return_annotation: TypeAnnotationSpec
    suite: str = Field(default="")
    function_type: FunctionType = Field(default=FunctionType.FUNCTION)

    @classmethod
    def create(
        cls,
        name: str,
        return_annotation: TypeAnnotationSpec,
        decorators: list[str] | None = None,
        parameters: list[ParameterSpec] | None = None,
        suite: str = "",
        function_type: FunctionType = FunctionType.FUNCTION,
    ):
        return cls(
            name=name,
            decorators=decorators or [],
            parameters=parameters or [],
            suite=suite,
            return_annotation=return_annotation,
            function_type=function_type,
        )

    @classmethod
    def parse_ast(cls, node: ast.FunctionDef | ast.AsyncFunctionDef, source_code: str):
        params: list[ParameterSpec] = []
        for arg in node.args.args:
            anno = TypeAnnotationSpec.parse_ast(arg.annotation)
            params.append(ParameterSpec(name=arg.arg, annotation=anno))

        return_anno = TypeAnnotationSpec.parse_ast(node.returns)
        full_source = ast.get_source_segment(source_code, node)
        if full_source is None:
            suite_code = "..."
        else:
            suite_code = full_source[node.body[0].lineno - 1 : node.body[-1].lineno]
        decorators = [ast.unparse(decorator) for decorator in node.decorator_list]

        # Determine function type
        function_type = FunctionType.FUNCTION
        if "classmethod" in decorators:
            function_type = FunctionType.CLASS_METHOD
        elif "staticmethod" in decorators:
            function_type = FunctionType.STATIC_METHOD
        elif params and params[0].name == "self":
            function_type = FunctionType.INSTANCE_METHOD
            params = params[1:]

        return cls.create(
            name=node.name,
            return_annotation=return_anno,
            decorators=decorators,
            parameters=params,
            suite=suite_code,
            function_type=function_type,
        )

    def get_required_types(self) -> set[str]:
        types: set[str] = set()
        types.update(self.return_annotation.get_all_referenced_names())
        types.update(self.decorators)
        for p in self.parameters:
            types.update(p.annotation.get_all_referenced_names())
        return types

    def is_instance_method(self) -> bool:
        return self.function_type == FunctionType.INSTANCE_METHOD
