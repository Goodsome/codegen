from __future__ import annotations
from typing import Annotated

from pydantic import Field, TypeAdapter
from .ast_return import AstReturn
from .ast_assert import AstAssert
from .ast_assign import AstAssign
from .ast_ann_assign import AstAnnAssign
from .ast_aug_assign import AstAugAssign
from .ast_async_function_def import AstAsyncFunctionDef
from .ast_expr_stmt import AstExprStmt
from .ast_for import AstFor
from .ast_while import AstWhile
from .ast_function_def import AstFunctionDef
from .ast_if import AstIf
from .ast_with import AstWith
from .ast_raise import AstRaise
from .ast_pass import AstPass
from .ast_break import AstBreak
from .ast_continue import AstContinue
from .ast_match import AstMatch
from .ast_try import AstTry
from .ast_import import AstImport
from .ast_import_from import AstImportFrom
from .ast_class_def import AstClassDef

AstStmt = Annotated[
    AstReturn | AstRaise | AstAssert | AstPass | AstBreak | AstContinue
    | AstAssign | AstAnnAssign | AstAugAssign | AstExprStmt
    | AstFor | AstWhile | AstIf | AstWith | AstMatch | AstTry
    | AstFunctionDef | AstAsyncFunctionDef
    | AstImport | AstImportFrom
    | AstClassDef,
    Field(discriminator="kind")
]

ast_stmt_adapter: TypeAdapter[AstStmt] = TypeAdapter(AstStmt)