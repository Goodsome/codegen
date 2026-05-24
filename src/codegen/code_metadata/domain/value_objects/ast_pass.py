from dataclasses import dataclass

from codegen.code_metadata.domain.core.ast_stmt import AstStmt


@dataclass
class AstPass(AstStmt):
    """Represents an ast.Pass node."""
    pass
