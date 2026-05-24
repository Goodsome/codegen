import ast

from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.domain.value_objects.lambda_args import LambdaArgs


class AstToLambdaArgs:

    @staticmethod
    def to_lambda_args(node: ast.arguments) -> LambdaArgs:
        return LambdaArgs(
            posonlyargs=[AstToLambdaArgs._to_arg(a) for a in node.posonlyargs],
            args=[AstToLambdaArgs._to_arg(a) for a in node.args],
            vararg=AstToLambdaArgs._to_arg(node.vararg) if node.vararg else None,
            kwonlyargs=[AstToLambdaArgs._to_arg(a) for a in node.kwonlyargs],
            kw_defaults=[
                ast.unparse(d) if d is not None else None
                for d in node.kw_defaults
            ],
            kwarg=AstToLambdaArgs._to_arg(node.kwarg) if node.kwarg else None,
            defaults=[
                ast.unparse(d) if d is not None else None
                for d in node.defaults
            ],
        )

    @staticmethod
    def _to_arg(node: ast.arg) -> Arg:
        return Arg(
            arg=node.arg,
            annotation=getattr(node.annotation, "id", None) or (ast.unparse(node.annotation) if node.annotation else None),
            type_comment=node.type_comment,
        )
