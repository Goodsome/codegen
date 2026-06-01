from __future__ import annotations
from typing import TYPE_CHECKING
from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects import AstExpr

class AstKeyword(ValueObject):

    arg: str | None
    value: AstExpr
    