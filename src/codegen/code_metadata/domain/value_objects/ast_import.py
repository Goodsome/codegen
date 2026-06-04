from __future__ import annotations

from typing import Literal

from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core import ValueObject

from .ast_alias import AstAlias


class AstImport(ValueObject):
    kind: Literal[AstStmtKind.IMPORT] = AstStmtKind.IMPORT
    names: list[AstAlias]
