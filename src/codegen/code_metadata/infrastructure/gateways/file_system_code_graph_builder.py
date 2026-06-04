from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
    GetProjectDocumentsQuery,
)
from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDto,
    DirectoryNodeDto,
    FileNodeDto,
    ModuleNodeDto,
    OutboundEdgeDto,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.domain.enums.edge_type import EdgeType


@dataclass
class FileSystemCodeGraphBuilder(CodeGraphBuilder):
    """从文件系统构建 CodeNode 图的实现。

    通过 GetProjectDocumentsHandler 获取项目文档列表，
    再从文档路径派生目录树结构，同步完成节点构造和 CONTAINS 边的建立。
    """

    get_project_documents: GetProjectDocumentsHandler

    @override
    def build(self, fqn_prefix: str) -> list[CodeNodeDto]:
        context_path = Path(fqn_prefix)
        nodes: list[CodeNodeDto] = []
        fqn_to_dto: dict[str, DirectoryNodeDto] = {}

        # 1. 获取项目文档
        query = GetProjectDocumentsQuery(dir_path=context_path)
        result = self.get_project_documents.handle(query)

        # 2. 收集所有唯一目录路径（从文档路径的 parent 链派生）
        dir_paths: set[Path] = set()
        for doc in result.code_documents:
            parent = doc.physical_path.parent
            while parent != context_path and context_path in parent.parents:
                dir_paths.add(parent)
                parent = parent.parent

        # 3. 创建根目录节点
        root_dto = self._build_directory_dto(context_path, fqn_to_dto)
        nodes.append(root_dto)

        # 4. 按深度排序创建目录节点，确保父目录先于子目录创建
        for dir_path in sorted(dir_paths, key=lambda p: len(p.parts)):
            nodes.append(self._build_directory_dto(dir_path, fqn_to_dto))

        # 5. 为每个文档创建 FileNode + ModuleNode
        for doc in result.code_documents:
            nodes.extend(self._build_file_dto(doc.physical_path, fqn_to_dto))

        return nodes

    def _build_directory_dto(
        self, path: Path, fqn_to_dto: dict[str, DirectoryNodeDto]
    ) -> DirectoryNodeDto:
        fqn = self._dir_fqn(path)
        dto = DirectoryNodeDto(fqn=fqn, name=path.name or fqn)
        fqn_to_dto[fqn] = dto

        # 为父目录添加 CONTAINS 边
        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in fqn_to_dto:
            fqn_to_dto[parent_fqn].outbound_edges.append(
                OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
            )

        return dto

    def _build_file_dto(
        self, path: Path, fqn_to_dto: dict[str, DirectoryNodeDto]
    ) -> list[CodeNodeDto]:
        fqn = self._file_fqn(path)
        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in fqn_to_dto:
            fqn_to_dto[parent_fqn].outbound_edges.append(
                OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
            )
        file_dto = FileNodeDto(fqn=fqn, name=path.name)
        module_dto = self._build_module_node_dto(path)
        file_dto.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.DEFINES_MODULE, target_fqn=module_dto.fqn)
        )
        return [file_dto, module_dto]

    def _build_module_node_dto(self, path: Path) -> ModuleNodeDto:
        module_fqn = self._module_fqn(path)
        return ModuleNodeDto(fqn=module_fqn, name=module_fqn.rsplit(".", maxsplit=1)[-1])

    def _dir_fqn(self, path: Path) -> str:
        """目录 FQN：相对路径/，以 / 结尾。根目录为 /。"""
        if path == Path("."):
            return "/"
        return f"{path.as_posix()}/"

    def _file_fqn(self, path: Path) -> str:
        """文件 FQN：相对文件路径。"""
        return path.as_posix()

    def _module_fqn(self, path: Path) -> str:
        """模块 FQN：将路径分隔符替换为 '.'，去除后缀。

        __init__.py 映射到其所在目录的包名(如 src/foo/__init__.py → src.foo),
        其余文件映射到模块路径(如 src/foo/bar.py → src.foo.bar)。
        """
        if path.name == "__init__.py":
            return ".".join(path.parent.parts)
        return ".".join(path.with_suffix("").parts)
