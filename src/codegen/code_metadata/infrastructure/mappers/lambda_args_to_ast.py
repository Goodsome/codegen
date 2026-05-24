import ast

from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.domain.value_objects.lambda_args import LambdaArgs


class LambdaArgsToAst:

    @staticmethod
    def to_node(args: LambdaArgs) -> ast.arguments:
        return ast.arguments(
            posonlyargs=[LambdaArgsToAst._to_arg(a) for a in args.posonlyargs],
            args=[LambdaArgsToAst._to_arg(a) for a in args.args],
            vararg=LambdaArgsToAst._to_arg(args.vararg) if args.vararg else None,
            kwonlyargs=[LambdaArgsToAst._to_arg(a) for a in args.kwonlyargs],
            kw_defaults=[
                ast.parse(d, mode="eval").body if d is not None else None
                for d in args.kw_defaults
            ],
            kwarg=LambdaArgsToAst._to_arg(args.kwarg) if args.kwarg else None,
            defaults=[
                ast.parse(d, mode="eval").body if d is not None else None
                for d in args.defaults
            ],
        )

    @staticmethod
    def _to_arg(arg: Arg) -> ast.arg:
        annotation = ast.Name(id=arg.annotation, ctx=ast.Load()) if arg.annotation else None
        return ast.arg(arg=arg.arg, annotation=annotation, type_comment=arg.type_comment)
