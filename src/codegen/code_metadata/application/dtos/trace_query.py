from pydantic import BaseModel

from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.enums.trace_direction import TraceDirection


class TraceSymbolDependenciesQuery(BaseModel):
    """CQRS 查询 DTO：追踪符号依赖关系。"""

    target_fqn: str
    direction: TraceDirection
    edge_type: EdgeType | None = None
