from typing import Any, Literal

from pydantic import field_serializer, field_validator

from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.shared.domain.core import ValueObject

_ELLIPSIS_MARKER = "__ellipsis__"


class AstConstant(ValueObject):
    kind: Literal[AstExprKind.CONSTANT] = AstExprKind.CONSTANT
    value: Any

    @field_serializer("value")
    @classmethod
    def _serialize_value(cls, v: Any) -> Any:
        if v is ...:
            return _ELLIPSIS_MARKER
        return v

    @field_validator("value", mode="before")
    @classmethod
    def _validate_value(cls, v: Any) -> Any:
        if v == _ELLIPSIS_MARKER:
            return ...
        return v
