from abc import ABC, abstractmethod

from codegen.code_metadata.application.dtos.bulk_save_result import BulkSaveResult
from codegen.code_metadata.domain.aggregates.code_node import CodeNode


class CodeNodeSyncService(ABC):
    """应用层 Port：批量同步 CodeNode 图。

    绕过领域层的聚合根生命周期，直接以 DTO 为单位执行
    高性能的批量 UPSERT 和边替换。适用于全量扫描入库场景。
    """

    @abstractmethod
    def save_nodes_bulk(
        self,
        node_dtos: list[CodeNode],
        sync_id: str,
        fqn_prefix: str,
    ) -> BulkSaveResult:
        """批量 UPSERT 节点，并全量替换其出边。

        内部流程：
        1. 以 FQN 为自然键执行 UPSERT（存在则更新，不存在则插入）。
        2. 将每个节点的 last_sync_id 标记为 sync_id（Mark 阶段）。
        3. 查询 FQN → 数据库实际 ID 的映射。
        4. 将 Edge.fqn 解析为 target_id。
        5. 清空旧出边 → 批量插入新出边。

        Returns:
            BulkSaveResult，包含 upsert 的节点数和新建的边数。
        """
        ...

    @abstractmethod
    def delete_stale_nodes(
        self,
        fqn_prefix: str,
        current_sync_id: str,
    ) -> int:
        """清除幽灵节点（Sweep 阶段）。

        删除所有 FQN 以 fqn_prefix 开头、但 last_sync_id 不等于
        current_sync_id 的节点。由于边表设置了 ondelete="CASCADE"，
        被删节点的所有出边/入边会被数据库自动级联清理。

        Returns:
            被删除的节点数量。
        """
        ...
