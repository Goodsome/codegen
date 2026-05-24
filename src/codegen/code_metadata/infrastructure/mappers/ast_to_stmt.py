import ast
from typing import overload

from codegen.code_metadata.domain.core.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_aug_assign import AstAugAssign
from codegen.code_metadata.domain.value_objects.ast_continue import AstContinue
from codegen.code_metadata.domain.value_objects.ast_expr_stmt import AstExprStmt
from codegen.code_metadata.domain.value_objects.ast_for import AstFor
from codegen.code_metadata.domain.value_objects.ast_if import AstIf
from codegen.code_metadata.domain.value_objects.ast_match import AstMatch
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase
from codegen.code_metadata.domain.value_objects.ast_pass import AstPass
from codegen.code_metadata.domain.value_objects.ast_raise import AstRaise
from codegen.code_metadata.domain.value_objects.ast_return import AstReturn
from codegen.code_metadata.domain.value_objects.ast_with import AstWith
from codegen.code_metadata.domain.value_objects.ast_with_item import AstWithItem
from codegen.code_metadata.infrastructure.mappers.ast_to_expr import AstToExpr


class AstToStmt:

    @staticmethod
    def to_stmt(node: ast.stmt) -> AstStmt:
        match node:
            case ast.Return():
                return AstToStmt.to_ast_return(node)
            case ast.Raise():
                return AstToStmt.to_ast_raise(node)
            case ast.Pass():
                return AstToStmt.to_ast_pass(node)
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
    def to_ast_pass(node: ast.Pass) -> AstPass:
        return AstPass()

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
            op=node.op,
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
                pattern=case.pattern,
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
