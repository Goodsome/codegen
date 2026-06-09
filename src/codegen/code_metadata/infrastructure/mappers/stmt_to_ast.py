import ast

from codegen.code_metadata.domain.value_objects import (
    AstAlias,
    AstAsyncFunctionDef,
    AstBreak,
    AstClassDef,
    AstImportFrom,
    AstStmt,
    AstAnnAssign,
    AstAssert,
    AstAssign,
    AstAugAssign,
    AstContinue,
    AstExceptHandler,
    AstExprStmt,
    AstFor,
    AstFunctionDef,
    AstIf,
    AstMatch,
    AstMatchCase,
    AstPass,
    AstRaise,
    AstReturn,
    AstTry,
    AstWith,
    AstWithItem,
)
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.infrastructure.mappers._convert import binop_to_ast
from codegen.code_metadata.infrastructure.mappers.arguments_to_ast import ArgumentsToAst
from codegen.code_metadata.infrastructure.mappers.match_pattern_to_ast import MatchPatternToAst
from codegen.code_metadata.infrastructure.mappers.expr_to_ast import ExprToAst


class StmtToAst:

    @staticmethod
    def _fix_pos(node: ast.stmt) -> ast.stmt:
        if not hasattr(node, "lineno"):
            ast.fix_missing_locations(node)
        return node

    @staticmethod
    def to_node(stmt: AstStmt) -> ast.stmt:
        match stmt:
            case AstReturn():
                node = StmtToAst.from_return(stmt)
            case AstRaise():
                node = StmtToAst.from_raise(stmt)
            case AstAssert():
                node = StmtToAst.from_assert(stmt)
            case AstPass():
                node = StmtToAst.from_pass(stmt)
            case AstContinue():
                node = StmtToAst.from_continue(stmt)
            case AstWith():
                node = StmtToAst.from_with(stmt)
            case AstAssign():
                node = StmtToAst.from_assign(stmt)
            case AstAnnAssign():
                node = StmtToAst.from_ann_assign(stmt)
            case AstAugAssign():
                node = StmtToAst.from_aug_assign(stmt)
            case AstFor():
                node = StmtToAst.from_for(stmt)
            case AstIf():
                node = StmtToAst.from_if(stmt)
            case AstMatch():
                node = StmtToAst.from_match(stmt)
            case AstExprStmt():
                node = StmtToAst.from_expr_stmt(stmt)
            case AstBreak():
                node = StmtToAst.from_break(stmt)
            case AstTry():
                node = StmtToAst.from_try(stmt)
            case AstFunctionDef():
                node = StmtToAst.from_function_def(stmt)
            case AstAsyncFunctionDef():
                node = StmtToAst.from_async_function_def(stmt)
            case AstClassDef():
                node = StmtToAst.from_class_def(stmt)
            case AstImport():
                node = StmtToAst.from_import(stmt)
            case AstImportFrom():
                node = StmtToAst.from_import_from(stmt)
            case _:
                raise NotImplementedError(f"Unsupported AstStmt type: {type(stmt)}")
        return StmtToAst._fix_pos(node)

    @staticmethod
    def from_import(stmt: AstImport) -> ast.Import:
        return ast.Import(
            names=[StmtToAst.from_alias(n) for n in stmt.names],
        )

    @staticmethod
    def from_import_from(stmt: AstImportFrom) -> ast.ImportFrom:
        return ast.ImportFrom(
            module=stmt.module,
            names=[StmtToAst.from_alias(n) for n in stmt.names],
            level=stmt.level,
        )
    
    @staticmethod
    def from_alias(stmt: AstAlias) -> ast.alias:
        return ast.alias(
            name=stmt.name,
            asname=stmt.asname,
        )

    @staticmethod
    def from_class_def(stmt: AstClassDef) -> ast.ClassDef:
        return ast.ClassDef(
            name=stmt.name,
            bases=[ExprToAst.to_node(b) for b in stmt.bases],
            keywords=[],
            body=[StmtToAst.to_node(s) for s in stmt.body],
        )

    @staticmethod
    def _to_with_item(item: AstWithItem) -> ast.withitem:
        return ast.withitem(
            context_expr=ExprToAst.to_node(item.context_expr),
            optional_vars=ExprToAst.to_node(item.optional_vars),
        )

    @staticmethod
    def _to_match_case(case: AstMatchCase) -> ast.match_case:
        return ast.match_case(
            pattern=MatchPatternToAst.to_node(case.pattern),
            guard=ExprToAst.to_node(case.guard),
            body=[StmtToAst.to_node(s) for s in case.body],
        )

    @staticmethod
    def _to_body(stmts: list[AstStmt]) -> list[ast.stmt]:
        return [StmtToAst.to_node(s) for s in stmts]

    @staticmethod
    def from_return(stmt: AstReturn) -> ast.Return:
        return ast.Return(value=ExprToAst.to_node(stmt.value))

    @staticmethod
    def from_raise(stmt: AstRaise) -> ast.Raise:
        return ast.Raise(
            exc=ExprToAst.to_node(stmt.exc),
            cause=ExprToAst.to_node(stmt.cause),
        )

    @staticmethod
    def from_assert(stmt: AstAssert) -> ast.Assert:
        return ast.Assert(
            test=ExprToAst.to_node(stmt.test),
            msg=ExprToAst.to_node(stmt.msg),
        )

    @staticmethod
    def from_pass(stmt: AstPass) -> ast.Pass:
        return ast.Pass()

    @staticmethod
    def from_continue(stmt: AstContinue) -> ast.Continue:
        return ast.Continue()

    @staticmethod
    def from_break(stmt: AstBreak) -> ast.Break:
        return ast.Break()

    @staticmethod
    def from_with(stmt: AstWith) -> ast.With:
        return ast.With(
            items=[StmtToAst._to_with_item(item) for item in stmt.items],
            body=StmtToAst._to_body(stmt.body),
        )

    @staticmethod
    def from_assign(stmt: AstAssign) -> ast.Assign:
        return ast.Assign(
            targets=[ExprToAst.to_node(t) for t in stmt.targets],
            value=ExprToAst.to_node(stmt.value),
        )

    @staticmethod
    def from_ann_assign(stmt: AstAnnAssign) -> ast.AnnAssign:
        return ast.AnnAssign(
            target=ExprToAst.to_node(stmt.target),
            annotation=ExprToAst.to_node(stmt.annotation),
            value=ExprToAst.to_node(stmt.value),
            simple=stmt.simple,
        )

    @staticmethod
    def from_aug_assign(stmt: AstAugAssign) -> ast.AugAssign:
        return ast.AugAssign(
            target=ExprToAst.to_node(stmt.target),
            op=binop_to_ast(stmt.op),
            value=ExprToAst.to_node(stmt.value),
        )

    @staticmethod
    def from_for(stmt: AstFor) -> ast.For:
        return ast.For(
            target=ExprToAst.to_node(stmt.target),
            iter=ExprToAst.to_node(stmt.iter),
            body=StmtToAst._to_body(stmt.body),
            orelse=StmtToAst._to_body(stmt.orelse),
        )

    @staticmethod
    def from_if(stmt: AstIf) -> ast.If:
        return ast.If(
            test=ExprToAst.to_node(stmt.test),
            body=StmtToAst._to_body(stmt.body),
            orelse=StmtToAst._to_body(stmt.orelse),
        )

    @staticmethod
    def from_match(stmt: AstMatch) -> ast.Match:
        return ast.Match(
            subject=ExprToAst.to_node(stmt.subject),
            cases=[StmtToAst._to_match_case(c) for c in stmt.cases],
        )

    @staticmethod
    def from_expr_stmt(stmt: AstExprStmt) -> ast.Expr:
        return ast.Expr(value=ExprToAst.to_node(stmt.value))

    @staticmethod
    def _to_except_handler(handler: AstExceptHandler) -> ast.ExceptHandler:
        return ast.ExceptHandler(
            type=ExprToAst.to_node(handler.type),
            name=handler.name,
            body=StmtToAst._to_body(handler.body),
        )

    @staticmethod
    def from_try(stmt: AstTry) -> ast.Try:
        return ast.Try(
            body=StmtToAst._to_body(stmt.body),
            handlers=[StmtToAst._to_except_handler(h) for h in stmt.handlers],
            orelse=StmtToAst._to_body(stmt.orelse),
            finalbody=StmtToAst._to_body(stmt.finalbody),
        )

    @staticmethod
    def from_function_def(stmt: AstFunctionDef) -> ast.FunctionDef:
        return ast.FunctionDef(
            name=stmt.name,
            args=ArgumentsToAst.to_node(stmt.args),
            body=StmtToAst._to_body(stmt.body),
            decorator_list=[ExprToAst.to_node(d) for d in stmt.decorator_list],
            returns=ExprToAst.to_node(stmt.returns) if stmt.returns else None,
            type_comment=stmt.type_comment,
        )

    @staticmethod
    def from_async_function_def(stmt: AstAsyncFunctionDef) -> ast.AsyncFunctionDef:
        return ast.AsyncFunctionDef(
            name=stmt.name,
            args=ArgumentsToAst.to_node(stmt.args),
            body=StmtToAst._to_body(stmt.body),
            decorator_list=[ExprToAst.to_node(d) for d in stmt.decorator_list],
            returns=ExprToAst.to_node(stmt.returns) if stmt.returns else None,
            type_comment=stmt.type_comment,
        )
