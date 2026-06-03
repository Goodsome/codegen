from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDto,
    DirectoryNodeDto,
    FileNodeDto,
    ModuleNodeDto,
    OutboundEdgeDto,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
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
        fqn_to_dto: dict[str, DirectoryNodeDto] = {}

        nodes.extend(self._build_dto(context_path, fqn_to_dto))

        for dirpath, dirnames, filenames in context_path.walk():
            dirnames[:] = sorted(d for d in dirnames if d not in _IGNORE_DIRS)

            for dname in dirnames:
                nodes.extend(self._build_dto(dirpath / dname, fqn_to_dto))

            for fname in sorted(filenames):
                nodes.extend(self._build_dto(dirpath / fname, fqn_to_dto))

        return nodes

    def _build_dto(self, path: Path, fqn_to_dto: dict[str, DirectoryNodeDto]) -> list[CodeNodeDto]:
        fqn = self._dir_fqn(path) if path.is_dir() else self._file_fqn(path)
        name = path.name
        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in fqn_to_dto:
            parent_dto = fqn_to_dto[parent_fqn]
            parent_dto.outbound_edges.append(
                OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
            )
        if path.is_dir():
            dto = DirectoryNodeDto(fqn=fqn, name=name)
            fqn_to_dto[fqn] = dto
            return [dto]
        file_dto = FileNodeDto(fqn=fqn, name=name)
        module_dto = self._build_module_node_dto(path)
        file_dto.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.DEFINES_MODULE, target_fqn=module_dto.fqn)
        )
        return [file_dto, module_dto]

    def _build_module_node_dto(self, path: Path) -> ModuleNodeDto:
        module_fqn = self._module_fqn(path)
        return ModuleNodeDto(fqn=module_fqn, name=module_fqn.rsplit(".", maxsplit=1)[-1])

    def _dir_fqn(self, path: Path) -> str:
        """目录 FQN：context_name/相对路径/，以 / 结尾。"""
        rel = path.relative_to(self.root).as_posix()
        return f"{rel}/"

    def _file_fqn(self, path: Path) -> str:
        """文件 FQN：context_name/相对文件路径。"""
        rel = path.relative_to(self.root).as_posix()
        return f"{rel}"

    def _module_fqn(self, path: Path) -> str:
        """模块 FQN：将路径分隔符替换为 '.'，去除后缀。

        __init__.py 映射到其所在目录的包名（如 src/foo/__init__.py → src.foo），
        其余文件映射到模块路径（如 src/foo/bar.py → src.foo.bar）。
        """
        rel = path.relative_to(self.root)
        if path.name == "__init__.py":
            return ".".join(rel.parent.parts)
        return ".".join(rel.with_suffix("").parts)