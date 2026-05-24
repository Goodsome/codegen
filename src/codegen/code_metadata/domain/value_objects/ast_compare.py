from dataclasses import dataclass, field
import ast

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstCompare(AstExpr):
    """Represents an ast.Compare node."""

    left: AstExpr
    ops: list[ast.cmpop] = field(default_factory=list)
    comparators: list[AstExpr] = field(default_factory=list)
