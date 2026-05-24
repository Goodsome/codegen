from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstAttribute(AstExpr):
    """Represents an ast.Attribute node (e.g., obj.attr)."""

    value: AstExpr
    attr: str
