from abc import ABC, abstractmethod
from uuid import UUID

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto, CodeNodeDetailDto
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind


class CodeNodeQueryService(ABC):
    """CodeNode 的 CQRS 读侧端口：直接查询 DTO，不经过领域模型。"""

    @abstractmethod
    def find_by_fqn_prefix(self, fqn_prefix: str) -> list[CodeNodeDto]:
        """查询 fqn 以指定前缀开头的所有 CodeNodeDto（含根节点自身）。"""
        pass

    @abstractmethod
    def find_by_fqn(self, fqn: str) -> CodeNodeDetailDto | None:
        """按 FQN 查询单个 CodeNode 的详情（含入边和出边）。"""
        pass

    @abstractmethod
    def find_by_id(self, node_id: UUID) -> CodeNodeDetailDto | None:
        """按 ID 查询单个 CodeNode 的详情（含入边和出边）。"""
        pass

    @abstractmethod
    def find_unused_nodes(self, kind: CodeNodeKind) -> list[CodeNodeDto]:
        """查询指定类型下未被使用的节点（支持 CLASS、FUNCTION、VARIABLE）。

        "未被使用"的判定逻辑：不存在类型为 IMPORTS 的入边。
        """
        pass
