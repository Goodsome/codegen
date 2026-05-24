from enum import StrEnum, auto


class AstStmtKind(StrEnum):
    RETURN = auto()
    RAISE = auto()
    PASS = auto()
    BREAK = auto()
    CONTINUE = auto()
    ASSIGN = auto()
    ANN_ASSIGN = auto()
    AUG_ASSIGN = auto()
    EXPR_STMT = auto()
    FOR = auto()
    IF = auto()
    WITH = auto()
    MATCH = auto()
