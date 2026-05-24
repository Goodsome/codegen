from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstName(AstExpr):
    """Represents an ast.Name node (variable/identifier reference)."""

    id: str
