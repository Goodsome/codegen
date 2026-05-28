import ast

from codegen.code_metadata.domain.value_objects import (
    AstStmt,
    AstAnnAssign,
    AstAssert,
    AstAssign,
    AstAugAssign,
    AstBreak,
    AstContinue,
    AstExprStmt,
    AstFor,
    AstIf,
    AstMatch,
    AstMatchCase,
    AstPass,
    AstRaise,
    AstReturn,
    AstWith,
    AstWithItem,
)
from codegen.code_metadata.infrastructure.mappers._convert import binop_from_ast
from codegen.code_metadata.infrastructure.mappers.ast_to_match_pattern import AstToMatchPattern
from codegen.code_metadata.infrastructure.mappers.ast_to_expr import AstToExpr


class AstToStmt:

    @staticmethod
    def to_stmt(node: ast.stmt) -> AstStmt:
        match node:
            case ast.Return():
                return AstToStmt.to_ast_return(node)
            case ast.Raise():
                return AstToStmt.to_ast_raise(node)
            case ast.Assert():
                return AstToStmt.to_ast_assert(node)
            case ast.Pass():
                return AstToStmt.to_ast_pass(node)
            case ast.Break():
                return AstToStmt.to_ast_break(node)
            case ast.Continue():
                return AstToStmt.to_ast_continue(node)
            case ast.With():
                return AstToStmt.to_ast_with(node)
            case ast.Assign():
                return AstToStmt.to_ast_assign(node)
            case ast.AnnAssign():
                return AstToStmt.to_ast_ann_assign(node)
            case ast.AugAssign():
                return AstToStmt.to_ast_aug_assign(node)
            case ast.For():
                return AstToStmt.to_ast_for(node)
            case ast.If():
                return AstToStmt.to_ast_if(node)
            case ast.Match():
                return AstToStmt.to_ast_match(node)
            case ast.Expr():
                return AstToStmt.to_ast_expr_stmt(node)
            case _:
                raise NotImplementedError(f"Unsupported AST node: {node}")

    @staticmethod
    def to_ast_return(node: ast.Return) -> AstReturn:
        return AstReturn(value=AstToExpr.to_expr(node.value))

    @staticmethod
    def to_ast_raise(node: ast.Raise) -> AstRaise:
        return AstRaise(
            exc=AstToExpr.to_expr(node.exc),
            cause=AstToExpr.to_expr(node.cause),
        )

    @staticmethod
    def to_ast_assert(node: ast.Assert) -> AstAssert:
        return AstAssert(
            test=AstToExpr.to_expr(node.test),
            msg=AstToExpr.to_expr(node.msg),
        )

    @staticmethod
    def to_ast_pass(node: ast.Pass) -> AstPass:
        return AstPass()

    @staticmethod
    def to_ast_break(node: ast.Break) -> AstBreak:
        return AstBreak()

    @staticmethod
    def to_ast_continue(node: ast.Continue) -> AstContinue:
        return AstContinue()

    @staticmethod
    def to_ast_with(node: ast.With) -> AstWith:
        items = [
            AstWithItem(
                context_expr=AstToExpr.to_expr(item.context_expr),
                optional_vars=AstToExpr.to_expr(item.optional_vars),
            )
            for item in node.items
        ]
        body = [AstToStmt.to_stmt(stmt) for stmt in node.body]
        return AstWith(items=items, body=body)

    @staticmethod
    def to_ast_assign(node: ast.Assign) -> AstAssign:
        targets = [AstToExpr.to_expr(target) for target in node.targets]
        return AstAssign(targets=targets, value=AstToExpr.to_expr(node.value))

    @staticmethod
    def to_ast_ann_assign(node: ast.AnnAssign) -> AstAnnAssign:
        return AstAnnAssign(
            target=AstToExpr.to_expr(node.target),
            annotation=AstToExpr.to_expr(node.annotation),
            value=AstToExpr.to_expr(node.value),
            simple=node.simple,
        )

    @staticmethod
    def to_ast_aug_assign(node: ast.AugAssign) -> AstAugAssign:
        return AstAugAssign(
            target=AstToExpr.to_expr(node.target),
            op=binop_from_ast(node.op),
            value=AstToExpr.to_expr(node.value),
        )

    @staticmethod
    def to_ast_for(node: ast.For) -> AstFor:
        return AstFor(
            target=AstToExpr.to_expr(node.target),
            iter=AstToExpr.to_expr(node.iter),
            body=[AstToStmt.to_stmt(stmt) for stmt in node.body],
            orelse=[AstToStmt.to_stmt(stmt) for stmt in node.orelse],
        )

    @staticmethod
    def to_ast_if(node: ast.If) -> AstIf:
        return AstIf(
            test=AstToExpr.to_expr(node.test),
            body=[AstToStmt.to_stmt(stmt) for stmt in node.body],
            orelse=[AstToStmt.to_stmt(stmt) for stmt in node.orelse],
        )

    @staticmethod
    def to_ast_match(node: ast.Match) -> AstMatch:
        cases = [
            AstMatchCase(
                pattern=AstToMatchPattern.to_match_pattern(case.pattern),
                guard=AstToExpr.to_expr(case.guard),
                body=[AstToStmt.to_stmt(stmt) for stmt in case.body],
            )
            for case in node.cases
        ]
        return AstMatch(
            subject=AstToExpr.to_expr(node.subject),
            cases=cases,
        )

    @staticmethod
    def to_ast_expr_stmt(node: ast.Expr) -> AstExprStmt:
        return AstExprStmt(value=AstToExpr.to_expr(node.value))
