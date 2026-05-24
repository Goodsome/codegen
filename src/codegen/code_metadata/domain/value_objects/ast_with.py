from dataclasses import dataclass, field

from codegen.code_metadata.domain.core.ast_stmt import AstStmt
from codegen.code_metadata.domain.value_objects.ast_with_item import AstWithItem


@dataclass
class AstWith(AstStmt):
    """Represents an ast.With node."""

    items: list[AstWithItem] = field(default_factory=list)
    body: list[AstStmt] = field(default_factory=list)
