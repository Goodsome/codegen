from abc import ABC, abstractmethod
from uuid import UUID

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto, CodeNodeDetailDto


class CodeNodeQueryService(ABC):
    """CodeNode 的 CQRS 读侧端口：直接查询 DTO，不经过领域模型。"""

    @abstractmethod
    def find_by_fqn_prefix(self, fqn_prefix: str) -> list[CodeNodeDto]:
        """查询 fqn 以指定前缀开头的所有 CodeNodeDto（含根节点自身）。"""
        pass

    @abstractmethod
    def find_by_id(self, node_id: UUID) -> CodeNodeDetailDto | None:
        """按 ID 查询单个 CodeNode 的详情（含入边和出边）。"""
        pass
