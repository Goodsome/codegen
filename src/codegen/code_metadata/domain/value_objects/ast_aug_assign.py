from typing import TYPE_CHECKING, Literal

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.enums.bin_op import BinOp
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstAugAssign(ValueObject):
    kind: Literal[AstStmtKind.AUG_ASSIGN] = AstStmtKind.AUG_ASSIGN
    target: "AstExpr"
    op: BinOp
    value: "AstExpr"
