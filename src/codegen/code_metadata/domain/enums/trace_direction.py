from enum import StrEnum, auto


class TraceDirection(StrEnum):
    """追踪方向：上游（依赖者）或下游（被依赖者）。"""

    UPSTREAM = auto()
    DOWNSTREAM = auto()
