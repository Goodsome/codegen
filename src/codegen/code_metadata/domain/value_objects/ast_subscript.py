from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstSubscript(AstExpr):
    """Represents an ast.Subscript node (e.g., obj[key])."""

    value: AstExpr
    slice: AstExpr
