from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstContinue(AstStmt):
    """Represents an ast.Continue node."""
    pass
