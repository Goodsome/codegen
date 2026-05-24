from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_expr import AstExpr


@dataclass
class AstDict(AstExpr):
    """Represents an ast.Dict node."""

    keys: list[AstExpr | None] = field(default_factory=list)
    values: list[AstExpr] = field(default_factory=list)
