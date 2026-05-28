from __future__ import annotations
from typing import Annotated

from pydantic import Field, TypeAdapter
from .ast_return import AstReturn
from .ast_assert import AstAssert
from .ast_assign import AstAssign
from .ast_ann_assign import AstAnnAssign
from .ast_aug_assign import AstAugAssign
from .ast_expr_stmt import AstExprStmt
from .ast_for import AstFor
from .ast_if import AstIf
from .ast_with import AstWith
from .ast_raise import AstRaise
from .ast_pass import AstPass
from .ast_break import AstBreak
from .ast_continue import AstContinue
from .ast_match import AstMatch

AstStmt = Annotated[
    AstReturn | AstRaise | AstAssert | AstPass | AstBreak | AstContinue
    | AstAssign | AstAnnAssign | AstAugAssign | AstExprStmt
    | AstFor | AstIf | AstWith | AstMatch,
    Field(discriminator="kind")
]

ast_stmt_adapter: TypeAdapter[AstStmt] = TypeAdapter(AstStmt)