from dataclasses import dataclass, field
from typing import TypeAlias

from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType


@dataclass
class OutboundEdgeDto:
    """边的 DTO：用 target_fqn 引用目标节点，而非 target_id。

    在构建阶段目标节点的数据库 ID 尚不可知，
    因此通过自然键（FQN）建立引用，由仓储层在持久化时解析为实际 ID。
    """

    type: EdgeType
    target_fqn: str


@dataclass
class _BaseNodeDto:
    fqn: str
    name: str
    outbound_edges: list[OutboundEdgeDto] = field(default_factory=list)
    

@dataclass
class DirectoryNodeDto(_BaseNodeDto):
    """目录节点的 DTO：kind 固定为 DIRECTORY。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.DIRECTORY, init=False)


@dataclass
class FileNodeDto(_BaseNodeDto):
    """文件节点的 DTO：kind 固定为 FILE。"""

    kind: CodeNodeKind = field(default=CodeNodeKind.FILE, init=False)


CodeNodeDto: TypeAlias = DirectoryNodeDto | FileNodeDto
