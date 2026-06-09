from abc import ABC, abstractmethod

from codegen.code_metadata.domain.aggregates.code_node import CodeNode


class CodeGraphBuilder(ABC):
    """应用层 Port：从文件系统构建 CodeNode 图。"""

    @abstractmethod
    def build(self, fqn_prefix: str) -> list[CodeNode]:
        """遍历指定上下文的目录树，返回完整的 CodeNode 列表。"""
        ...
