from dataclasses import dataclass
from uuid import UUID

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDetailDto
from codegen.code_metadata.application.ports.code_node_query_service import CodeNodeQueryService


@dataclass
class GetCodeNodeDetail:
    """按 ID 查询单个 CodeNode 的详情（含入边和出边）。"""

    query_service: CodeNodeQueryService

    def execute(self, node_id: UUID) -> CodeNodeDetailDto:
        dto = self.query_service.find_by_id(node_id)
        if dto is None:
            raise ValueError(f"CodeNode with id '{node_id}' not found")
        return dto
