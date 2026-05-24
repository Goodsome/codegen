from dataclasses import dataclass
from typing import Any

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstConstant(AstExpr):
    """Represents an ast.Constant node (literal value)."""

    value: Any
