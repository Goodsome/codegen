from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstFormattedValue(AstExpr):
    """Represents an ast.FormattedValue node (f-string expression)."""

    value: AstExpr
    conversion: int
    format_spec: AstExpr | None = None

