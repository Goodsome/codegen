from dataclasses import dataclass, field
from pathlib import Path
from typing import override

from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
    GetProjectDocumentsQuery,
)
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.dtos.code_node_dto import (
    ClassNodeDto,
    CodeNodeDto,
    DirectoryNodeDto,
    FileNodeDto,
    FunctionNodeDto,
    ModuleNodeDto,
    OutboundEdgeDto,
    VariableNodeDto,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt


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

        query = GetProjectDocumentsQuery(dir_path=context_path)
        result = self.get_project_documents.handle(query)

        acl = CodeGraphAcl(root_path=context_path)
        nodes = acl.build_nodes(result.code_documents)

        return nodes


@dataclass
class CodeGraphAcl:
    root_path: Path
    nodes: list[CodeNodeDto] = field(default_factory=list)
    fqn_to_dto: dict[str, CodeNodeDto] = field(default_factory=dict)

    def build_nodes(self, code_documents: list[CodeDocument]) -> list[CodeNodeDto]:
        self._build_directory_nodes(code_documents)
        self._build_file_nodes(code_documents)

        return self.nodes

    def _build_directory_nodes(self, code_documents: list[CodeDocument]) -> None:
        dir_paths: set[Path] = set()
        for doc in code_documents:
            parent = doc.physical_path.parent
            while parent != self.root_path and self.root_path in parent.parents:
                dir_paths.add(parent)
                parent = parent.parent

        for dir_path in sorted(dir_paths, key=lambda p: len(p.parts)):
            self._build_directory_node(dir_path)

    def _build_file_nodes(self, code_documents: list[CodeDocument]) -> None:
        for doc in code_documents:
            self._build_file_node(doc)

    def _build_directory_node(self, path: Path) -> DirectoryNodeDto:
        fqn = self._dir_fqn(path)
        dto = DirectoryNodeDto(fqn=fqn, name=path.name or fqn)
        # 为父目录添加 CONTAINS 边
        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in self.fqn_to_dto:
            self.fqn_to_dto[parent_fqn].outbound_edges.append(
                OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
            )

        self.fqn_to_dto[fqn] = dto
        self.nodes.append(dto)

        return dto

    def _build_file_node(self, code_document: CodeDocument) -> None:
        path = code_document.physical_path
        fqn = self._file_fqn(path)
        parent_fqn = self._dir_fqn(path.parent)
        if parent_fqn in self.fqn_to_dto:
            self.fqn_to_dto[parent_fqn].outbound_edges.append(
                OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=fqn)
            )
        file_dto = FileNodeDto(fqn=fqn, name=path.name)
        self.nodes.append(file_dto)

        self._build_module_node_node(code_document, file_dto)

    def _build_module_node_node(
        self, code_document: CodeDocument, file_node: FileNodeDto
    ) -> ModuleNodeDto:
        path = code_document.physical_path
        module_fqn = self._module_fqn(path)
        dto = ModuleNodeDto(fqn=module_fqn, name=module_fqn.rsplit(".", maxsplit=1)[-1])
        self.fqn_to_dto[module_fqn] = dto
        self.nodes.append(dto)
        file_node.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.DEFINES_MODULE, target_fqn=module_fqn)
        )

        for stmt in code_document.body:
            self._parse_stmt(stmt, dto)

        return dto

    def _parse_stmt(
        self, stmt: AstStmt, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        match stmt:
            case AstClassDef():
                self._parse_class_def(stmt, parent_node)
            case AstFunctionDef():
                self._parse_function_def(stmt, parent_node)
            case AstAnnAssign():
                self._parse_ann_assign(stmt, parent_node)
            case AstAssign():
                self._parse_assign(stmt, parent_node)
            case _:
                pass

    def _parse_class_def(
        self, class_def: AstClassDef, module_node: ModuleNodeDto | ClassNodeDto
    ) -> ClassNodeDto:
        class_fqn = f"{module_node.fqn}::{class_def.name}"
        dto = ClassNodeDto(fqn=class_fqn, name=class_def.name)
        module_node.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=class_fqn)
        )
        self.nodes.append(dto)
        for stmt in class_def.body:
            self._parse_stmt(stmt, dto)
        return dto

    def _parse_function_def(
        self, func_def: AstFunctionDef, module_node: ModuleNodeDto | ClassNodeDto
    ) -> FunctionNodeDto:
        func_fqn = f"{module_node.fqn}::{func_def.name}"
        dto = FunctionNodeDto(fqn=func_fqn, name=func_def.name)
        module_node.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=func_fqn)
        )
        self.nodes.append(dto)
        return dto

    def _build_variable_node(
        self, name: str, module_node: ModuleNodeDto | ClassNodeDto
    ) -> VariableNodeDto:
        var_fqn = f"{module_node.fqn}::{name}"
        dto = VariableNodeDto(fqn=var_fqn, name=name)
        module_node.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=var_fqn)
        )
        self.nodes.append(dto)
        return dto

    def _parse_ann_assign(
        self, ann_assign: AstAnnAssign, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        target = ann_assign.target
        if not isinstance(target, AstName):
            return
        var_fqn = f"{parent_node.fqn}::{target.id}"
        dto = VariableNodeDto(fqn=var_fqn, name=target.id)
        parent_node.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=var_fqn)
        )
        self.nodes.append(dto)

    def _parse_assign(
        self, assign: AstAssign, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        if not assign.targets:
            return
        if not len(assign.targets) == 1:
            return
        target = assign.targets[0]
        if not isinstance(target, AstName):
            return
        var_fqn = f"{parent_node.fqn}::{target.id}"
        dto = VariableNodeDto(fqn=var_fqn, name=target.id)
        parent_node.outbound_edges.append(
            OutboundEdgeDto(type=EdgeType.CONTAINS, target_fqn=var_fqn)
        )
        self.nodes.append(dto)

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
