from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_comprehension import AstComprehension


@dataclass
class AstListComp(AstExpr):
    """Represents an ast.ListComp node."""

    elt: AstExpr
    generators: list[AstComprehension] = field(default_factory=list)
