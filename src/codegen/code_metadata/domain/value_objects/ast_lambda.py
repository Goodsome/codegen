from dataclasses import dataclass
import ast

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstLambda(AstExpr):
    """Represents an ast.Lambda node."""

    args: ast.arguments
    body: AstExpr
