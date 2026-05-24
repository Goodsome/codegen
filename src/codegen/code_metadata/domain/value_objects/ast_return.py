from dataclasses import dataclass
from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstReturn(AstStmt):

    value: AstExpr | None
    