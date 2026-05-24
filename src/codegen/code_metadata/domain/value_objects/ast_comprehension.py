from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstComprehension:
    """Represents a comprehension clause in a list/set/dict comprehension."""

    target: AstExpr
    iter: AstExpr
    ifs: list[AstExpr] = field(default_factory=list)
    is_async: int = 0

