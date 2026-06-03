from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDto,
    OutboundEdgeDto,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType

_IGNORE_DIRS = frozenset({
    "__pycache__", ".git", ".venv", "node_modules",
    ".mypy_cache", ".ruff_cache", ".pytest_cache",
})

@dataclass
class FileSystemCodeGraphBuilder(CodeGraphBuilder):
    """从文件系统构建 CodeNode 图的实现。

    使用 Python 3.12+ 的 Path.walk() 迭代遍历目录树，
    同步完成节点构造和 CONTAINS 边的建立。
    """

    root: Path

    @override
    def build(self, fqn_prefix: str) -> list[CodeNodeDto]:
        context_path = self.root / fqn_prefix
        nodes: list[CodeNodeDto] = []
        fqn_to_dto: dict[str, CodeNodeDto] = {}

        # 核心修复：直接使用迭代器，移除 _walk 递归函数
        for dirpath, dirnames, filenames in context_path.walk():
            # 1. 过滤并排序（原地修改 dirnames 决定了 walk 接下来要进入的目录）
            dirnames[:] = sorted(d for d in dirnames if d not in _IGNORE_DIRS)

            # 2. 确定父节点 DTO
            parent_dto: CodeNodeDto | None = None
            if dirpath != context_path:
                parent_dto = fqn_to_dto.get(self._dir_fqn(dirpath))

            # 3. 构造子目录节点
            for dname in dirnames:
                fqn = self._dir_fqn(dirpath / dname)
                dto = CodeNodeDto(fqn=fqn, name=dname, kind=CodeNodeKind.DIRECTORY)
                if parent_dto is not None:
                    parent_dto.outbound_edges.append(
                        OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
                    )
                nodes.append(dto)
                fqn_to_dto[fqn] = dto

            # 4. 构造文件节点
            for fname in sorted(filenames):
                fqn = self._file_fqn(dirpath / fname)
                dto = CodeNodeDto(fqn=fqn, name=fname, kind=CodeNodeKind.FILE)
                if parent_dto is not None:
                    parent_dto.outbound_edges.append(
                        OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
                    )
                nodes.append(dto)
                fqn_to_dto[fqn] = dto

        return nodes

    def _dir_fqn(self, path: Path) -> str:
        """目录 FQN：context_name/相对路径/，以 / 结尾。"""
        rel = path.relative_to(self.root).as_posix()
        return f"{rel}/"

    def _file_fqn(self, path: Path) -> str:
        """文件 FQN：context_name/相对文件路径。"""
        rel = path.relative_to(self.root).as_posix()
        return f"{rel}"