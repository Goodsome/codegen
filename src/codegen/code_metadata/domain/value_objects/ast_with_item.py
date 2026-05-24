
from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstWithItem:
    """Represents a withitem in a with statement."""

    context_expr: AstExpr
    optional_vars: AstExpr | None = None