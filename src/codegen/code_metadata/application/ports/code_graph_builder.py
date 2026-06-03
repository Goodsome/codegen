from abc import ABC, abstractmethod

from codegen.code_metadata.application.dtos.code_node_dto import CodeNodeDto


class CodeGraphBuilder(ABC):
    """应用层 Port：从文件系统构建 CodeNode 图。

    遍历指定 bounded context 对应的目录树，将目录和文件
    转换为 CodeNodeDto（含 CONTAINS 边），供同步服务持久化。
    """

    @abstractmethod
    def build(self, fqn_prefix: str) -> list[CodeNodeDto]:
        """遍历指定上下文的目录树，返回完整的 CodeNode DTO 列表。"""
        ...
