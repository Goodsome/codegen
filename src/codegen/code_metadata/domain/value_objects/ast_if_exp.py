from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstIfExp(AstExpr):
    """Represents an ast.IfExp node (ternary expression)."""

    test: AstExpr
    body: AstExpr
    orelse: AstExpr
