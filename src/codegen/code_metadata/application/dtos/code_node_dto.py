from dataclasses import dataclass, field

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
class CodeNodeDto:
    """CodeNode 的 DTO：不含 id，仅携带自然键和业务数据。

    用于领域服务（CodeGraphBuilder）向仓储层传递扫描结果。
    仓储层负责将 DTO 转为带数据库 ID 的领域实体后持久化。
    """

    fqn: str
    name: str
    kind: CodeNodeKind
    outbound_edges: list[OutboundEdgeDto] = field(default_factory=list)
