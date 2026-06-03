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

        base_dto = self._build_dto(context_path, fqn_to_dto)
        nodes.append(base_dto)
        fqn_to_dto[base_dto.fqn] = base_dto

        for dirpath, dirnames, filenames in context_path.walk():
            dirnames[:] = sorted(d for d in dirnames if d not in _IGNORE_DIRS)

            for dname in dirnames:
                dto = self._build_dto(dirpath / dname, fqn_to_dto)
                nodes.append(dto)
                fqn_to_dto[dto.fqn] = dto

            for fname in sorted(filenames):
                dto = self._build_dto(dirpath / fname, fqn_to_dto)
                nodes.append(dto)
                fqn_to_dto[dto.fqn] = dto

        return nodes

    def _build_dto(self, path: Path, fqn_to_dto: dict[str, CodeNodeDto]) -> CodeNodeDto:
        fqn = self._dir_fqn(path) if path.is_dir() else self._file_fqn(path)
        name = path.name
        kind = CodeNodeKind.DIRECTORY if path.is_dir() else CodeNodeKind.FILE
        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in fqn_to_dto:
            parent_dto = fqn_to_dto[parent_fqn]
            parent_dto.outbound_edges.append(
                OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
            )
        return CodeNodeDto(fqn=fqn, name=name, kind=kind)

    def _dir_fqn(self, path: Path) -> str:
        """目录 FQN：context_name/相对路径/，以 / 结尾。"""
        rel = path.relative_to(self.root).as_posix()
        return f"{rel}/"

    def _file_fqn(self, path: Path) -> str:
        """文件 FQN：context_name/相对文件路径。"""
        rel = path.relative_to(self.root).as_posix()
        return f"{rel}"