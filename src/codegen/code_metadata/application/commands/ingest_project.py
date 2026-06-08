import uuid
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.ingest_project_command import (
    IngestProjectCommand,
)
from codegen.code_metadata.application.dtos.ingest_project_result import (
    IngestProjectResult,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.application.ports.code_node_sync_service import (
    CodeNodeSyncService,
)


@dataclass
class IngestProject:
    """将一个 bounded context 下的目录结构扫描入库为 CodeNode 图。

    采用 Mark-and-Sweep 算法处理增量同步：
    1. CodeGraphBuilder 构建图（产出 DTO，不含 ID）
    2. CodeNodeSyncService 批量 UPSERT 节点 + 全量替换边（Mark）
    3. CodeNodeSyncService 清除幽灵节点（Sweep）

    纯粹的编排者：不包含任何业务规则或领域状态计算。
    """

    graph_builder: CodeGraphBuilder
    sync_service: CodeNodeSyncService

    def execute(self, cmd: IngestProjectCommand) -> IngestProjectResult:
        sync_id = uuid.uuid4().hex
        fqn_prefix = "src/codegen/"
        module_fqn_prefix = "codegen."
        if cmd.prefix:
            fqn_prefix = f"src/codegen/{cmd.prefix}/"
            module_fqn_prefix = f"codegen.{cmd.prefix}."

        # 1. 构建图：遍历文件系统，产出 CodeNodeDto 列表
        node_dtos = self.graph_builder.build(fqn_prefix=fqn_prefix)

        # 2. Mark：批量 UPSERT 节点 + 全量替换出边
        bulk_result = self.sync_service.save_nodes_bulk(
            node_dtos, sync_id, fqn_prefix, module_fqn_prefix=module_fqn_prefix
        )

        # 3. Sweep：清除属于该上下文但未被本次扫描标记的幽灵节点
        deleted_count = self.sync_service.delete_stale_nodes(
            fqn_prefix, sync_id, module_fqn_prefix=module_fqn_prefix
        )

        return IngestProjectResult(
            nodes_created=bulk_result.nodes_upserted,
            edges_created=bulk_result.edges_created,
            nodes_deleted=deleted_count,
        )
