import ast
from typing import overload

from codegen.code_metadata.domain.value_objects import (
    AstExpr,
    AstAttribute,
    AstBinOp,
    AstBoolOp,
    AstCall,
    AstCompare,
    AstComprehension,
    AstConstant,
    AstDict,
    AstDictComp,
    AstFormattedValue,
    AstGeneratorExp,
    AstIfExp,
    AstJoinedStr,
    AstLambda,
    AstList,
    AstListComp,
    AstName,
    AstSet,
    AstSetComp,
    AstSlice,
    AstStarred,
    AstSubscript,
    AstTuple,
    AstUnaryOp,
    AstYield,
    AstYieldFrom,
)
from codegen.code_metadata.infrastructure.mappers._convert import (
    binop_from_ast,
    boolop_from_ast,
    cmpop_from_ast,
    ctx_from_ast,
    unaryop_from_ast,
)
from codegen.code_metadata.infrastructure.mappers.ast_to_lambda_args import AstToLambdaArgs


class AstToExpr:

    @overload
    @staticmethod
    def to_expr(node: None) -> None: ...

    @overload
    @staticmethod
    def to_expr(node: ast.expr) -> AstExpr: ...

    @staticmethod
    def to_expr(node: ast.expr | None) -> AstExpr | None:
        if node is None:
            return None
        match node:
            case ast.Constant():
                return AstToExpr.to_ast_constant(node)
            case ast.Name():
                return AstToExpr.to_ast_name(node)
            case ast.Attribute():
                return AstToExpr.to_ast_attribute(node)
            case ast.Call():
                return AstToExpr.to_ast_call(node)
            case ast.Lambda():
                return AstToExpr.to_ast_lambda(node)
            case ast.IfExp():
                return AstToExpr.to_ast_if_exp(node)
            case ast.BinOp():
                return AstToExpr.to_ast_bin_op(node)
            case ast.BoolOp():
                return AstToExpr.to_ast_bool_op(node)
            case ast.UnaryOp():
                return AstToExpr.to_ast_unary_op(node)
            case ast.Compare():
                return AstToExpr.to_ast_compare(node)
            case ast.JoinedStr():
                return AstToExpr.to_ast_joined_str(node)
            case ast.FormattedValue():
                return AstToExpr.to_ast_formatted_value(node)
            case ast.ListComp():
                return AstToExpr.to_ast_list_comp(node)
            case ast.SetComp():
                return AstToExpr.to_ast_set_comp(node)
            case ast.DictComp():
                return AstToExpr.to_ast_dict_comp(node)
            case ast.GeneratorExp():
                return AstToExpr.to_ast_generator_exp(node)
            case ast.Slice():
                return AstToExpr.to_ast_slice(node)
            case ast.Starred():
                return AstToExpr.to_ast_starred(node)
            case ast.Subscript():
                return AstToExpr.to_ast_subscript(node)
            case ast.Tuple():
                return AstToExpr.to_ast_tuple(node)
            case ast.List():
                return AstToExpr.to_ast_list(node)
            case ast.Set():
                return AstToExpr.to_ast_set(node)
            case ast.Dict():
                return AstToExpr.to_ast_dict(node)
            case ast.Yield():
                return AstToExpr.to_ast_yield(node)
            case ast.YieldFrom():
                return AstToExpr.to_ast_yield_from(node)
            case _:
                raise NotImplementedError(f"Unsupported node type: {type(node)}")

    @staticmethod
    def to_ast_constant(node: ast.Constant) -> AstConstant:
        return AstConstant(value=node.value)

    @staticmethod
    def to_ast_name(node: ast.Name) -> AstName:
        return AstName(id=node.id)

    @staticmethod
    def to_ast_attribute(node: ast.Attribute) -> AstAttribute:
        return AstAttribute(
            value=AstToExpr.to_expr(node.value),
            attr=node.attr,
        )

    @staticmethod
    def to_ast_call(node: ast.Call) -> AstCall:
        return AstCall(
            func=AstToExpr.to_expr(node.func),
            args=[AstToExpr.to_expr(arg) for arg in node.args],
            kwargs={kw.arg: AstToExpr.to_expr(kw.value) for kw in node.keywords if kw.arg},
        )

    @staticmethod
    def to_ast_lambda(node: ast.Lambda) -> AstLambda:
        return AstLambda(
            args=AstToLambdaArgs.to_lambda_args(node.args),
            body=AstToExpr.to_expr(node.body),
        )

    @staticmethod
    def to_ast_if_exp(node: ast.IfExp) -> AstIfExp:
        return AstIfExp(
            test=AstToExpr.to_expr(node.test),
            body=AstToExpr.to_expr(node.body),
            orelse=AstToExpr.to_expr(node.orelse),
        )

    @staticmethod
    def to_ast_bin_op(node: ast.BinOp) -> AstBinOp:
        return AstBinOp(
            left=AstToExpr.to_expr(node.left),
            op=binop_from_ast(node.op),
            right=AstToExpr.to_expr(node.right),
        )

    @staticmethod
    def to_ast_bool_op(node: ast.BoolOp) -> AstBoolOp:
        return AstBoolOp(
            op=boolop_from_ast(node.op),
            values=[AstToExpr.to_expr(value) for value in node.values],
        )

    @staticmethod
    def to_ast_unary_op(node: ast.UnaryOp) -> AstUnaryOp:
        return AstUnaryOp(
            op=unaryop_from_ast(node.op),
            operand=AstToExpr.to_expr(node.operand),
        )

    @staticmethod
    def to_ast_compare(node: ast.Compare) -> AstCompare:
        return AstCompare(
            left=AstToExpr.to_expr(node.left),
            ops=[cmpop_from_ast(op) for op in node.ops],
            comparators=[AstToExpr.to_expr(comp) for comp in node.comparators],
        )

    @staticmethod
    def to_ast_joined_str(node: ast.JoinedStr) -> AstJoinedStr:
        return AstJoinedStr(
            values=[AstToExpr.to_expr(value) for value in node.values],
        )

    @staticmethod
    def to_ast_formatted_value(node: ast.FormattedValue) -> AstFormattedValue:
        return AstFormattedValue(
            value=AstToExpr.to_expr(node.value),
            conversion=node.conversion,
            format_spec=AstToExpr.to_expr(node.format_spec) if node.format_spec else None,
        )

    @staticmethod
    def to_ast_list_comp(node: ast.ListComp) -> AstListComp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstListComp(
            elt=AstToExpr.to_expr(node.elt),
            generators=generators,
        )

    @staticmethod
    def to_ast_set_comp(node: ast.SetComp) -> AstSetComp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstSetComp(
            elt=AstToExpr.to_expr(node.elt),
            generators=generators,
        )

    @staticmethod
    def to_ast_dict_comp(node: ast.DictComp) -> AstDictComp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstDictComp(
            key=AstToExpr.to_expr(node.key),
            value=AstToExpr.to_expr(node.value),
            generators=generators,
        )

    @staticmethod
    def to_ast_generator_exp(node: ast.GeneratorExp) -> AstGeneratorExp:
        generators = [
            AstComprehension(
                target=AstToExpr.to_expr(gen.target),
                iter=AstToExpr.to_expr(gen.iter),
                ifs=[AstToExpr.to_expr(if_expr) for if_expr in gen.ifs],
                is_async=gen.is_async,
            )
            for gen in node.generators
        ]
        return AstGeneratorExp(
            elt=AstToExpr.to_expr(node.elt),
            generators=generators,
        )

    @staticmethod
    def to_ast_slice(node: ast.Slice) -> AstSlice:
        return AstSlice(
            lower=AstToExpr.to_expr(node.lower) if node.lower else None,
            upper=AstToExpr.to_expr(node.upper) if node.upper else None,
            step=AstToExpr.to_expr(node.step) if node.step else None,
        )

    @staticmethod
    def to_ast_starred(node: ast.Starred) -> AstStarred:
        return AstStarred(
            value=AstToExpr.to_expr(node.value),
            ctx=ctx_from_ast(node.ctx),
        )

    @staticmethod
    def to_ast_subscript(node: ast.Subscript) -> AstSubscript:
        return AstSubscript(
            value=AstToExpr.to_expr(node.value),
            slice=AstToExpr.to_expr(node.slice),
        )

    @staticmethod
    def to_ast_tuple(node: ast.Tuple) -> AstTuple:
        return AstTuple(
            elts=[AstToExpr.to_expr(elt) for elt in node.elts],
        )

    @staticmethod
    def to_ast_list(node: ast.List) -> AstList:
        return AstList(
            elts=[AstToExpr.to_expr(elt) for elt in node.elts],
        )

    @staticmethod
    def to_ast_set(node: ast.Set) -> AstSet:
        return AstSet(
            elts=[AstToExpr.to_expr(elt) for elt in node.elts],
        )

    @staticmethod
    def to_ast_dict(node: ast.Dict) -> AstDict:
        return AstDict(
            keys=[AstToExpr.to_expr(key) for key in node.keys],
            values=[AstToExpr.to_expr(value) for value in node.values],
        )

    @staticmethod
    def to_ast_yield(node: ast.Yield) -> AstYield:
        return AstYield(
            value=AstToExpr.to_expr(node.value) if node.value else None,
        )

    @staticmethod
    def to_ast_yield_from(node: ast.YieldFrom) -> AstYieldFrom:
        return AstYieldFrom(
            value=AstToExpr.to_expr(node.value),
        )
