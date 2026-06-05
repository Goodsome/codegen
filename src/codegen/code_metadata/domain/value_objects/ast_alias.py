from __future__ import annotations

from codegen.shared.domain.core import ValueObject


class AstAlias(ValueObject):
    name: str
    asname: str | None = None
    