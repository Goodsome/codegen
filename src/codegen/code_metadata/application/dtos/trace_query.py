from typing import Literal

from pydantic import BaseModel

from codegen.code_metadata.domain.enums.edge_type import EdgeType


class TraceSymbolDependenciesQuery(BaseModel):
    """CQRS 查询 DTO：追踪符号依赖关系。"""

    target_fqn: str
    direction: Literal["upstream", "downstream"]
    edge_type: EdgeType | None = None
