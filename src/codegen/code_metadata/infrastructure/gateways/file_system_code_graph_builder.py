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
    MethodNodeDto,
    ModuleNodeDto,
    VariableNodeDto,
)
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.infrastructure.gateways.module_build_context import ModuleBuildContext
from codegen.code_metadata.infrastructure.gateways.node_registry import NodeRegistry


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

        node_registry = NodeRegistry()

        acl = CodeGraphAcl(
            fqn_factory=FqnFactory(),
            root_path=context_path,
            node_registery=node_registry,
        )
        acl.build_nodes(result.code_documents)

        return node_registry.nodes

@dataclass
class CodeGraphAcl:
    fqn_factory: FqnFactory
    root_path: Path
    node_registery: NodeRegistry

    def build_nodes(self, code_documents: list[CodeDocument]) -> list[CodeNodeDto]:
        self._build_directory_nodes(code_documents)
        self._build_file_nodes(code_documents)
        self._build_edges(code_documents=code_documents)

        return self.node_registery.nodes

    def _build_edges(self, code_documents: list[CodeDocument]) -> None:
        for code_document in code_documents:
            module_fqn = self.fqn_factory.build_module_fqn(code_document.physical_path)
            module = self.node_registery.get_node(module_fqn)
            assert isinstance(module, ModuleNodeDto)
            module_builder = ModuleBuildContext(
                module, 
                code_document, 
                self.node_registery
            )
            module_builder.build()
            
    def _add_node(self, dto: CodeNodeDto) -> None:
        self.node_registery.add_node(dto)

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
        fqn = self.fqn_factory.build_dir_fqn(path)
        dto = DirectoryNodeDto(fqn=fqn, name=path.name or fqn)
        parent_fqn = self.fqn_factory.build_dir_fqn(path.parent)
        parent_node = self.node_registery.find_node(parent_fqn)
        if parent_node is not None:
            assert isinstance(parent_node, DirectoryNodeDto)
            parent_node.contains(dto)

        self._add_node(dto)

        return dto

    def _build_file_node(self, code_document: CodeDocument) -> None:
        path = code_document.physical_path
        fqn = self.fqn_factory.build_file_fqn(path)
        file_dto = FileNodeDto(fqn=fqn, name=path.name)

        parent_fqn = self.fqn_factory.build_dir_fqn(path.parent)
        parent_node = self.node_registery.find_node(parent_fqn)
        if parent_node is not None:
            assert isinstance(parent_node, DirectoryNodeDto)
            parent_node.contains(file_dto)

        self._add_node(file_dto)
        self._build_module_node(code_document, file_dto)

    def _build_module_node(
        self, code_document: CodeDocument, file_node: FileNodeDto
    ) -> ModuleNodeDto:
        path = code_document.physical_path
        module_fqn = self.fqn_factory.build_module_fqn(path)
        module_node = ModuleNodeDto(
            fqn=module_fqn,
            name=module_fqn.rsplit(".", maxsplit=1)[-1],
            is_package=path.name == "__init__.py",
        )
        self._add_node(module_node)
        file_node.defines_module(module_node)

        for stmt in code_document.body:
            self._parse_stmt(stmt, module_node)

        return module_node

    def _parse_stmt(
        self, stmt: AstStmt, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        match stmt:
            case AstClassDef():
                assert isinstance(parent_node, ModuleNodeDto)
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
        self, class_def: AstClassDef, module_node: ModuleNodeDto
    ) -> ClassNodeDto:
        class_fqn = f"{module_node.fqn}::{class_def.name}"
        node = ClassNodeDto(fqn=class_fqn, name=class_def.name)
        module_node.contains(node)
        for stmt in class_def.body:
            self._parse_stmt(stmt, node)

        self._add_node(node)
        return node


    def _parse_function_def(
        self, func_def: AstFunctionDef, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> FunctionNodeDto | MethodNodeDto:
        func_fqn = f"{parent_node.fqn}::{func_def.name}"
        if func_def.is_overload:
            func_fqn = f"{func_fqn}::<overload_{func_def.lineno}>"
        elif func_def.is_setter_property:
            func_fqn = f"{func_fqn}::<setter>"
        elif func_def.is_deleter_property:
            func_fqn = f"{func_fqn}::<deleter>"
        elif func_def.is_expression_property:
            func_fqn = f"{func_fqn}::<expression>"

        match parent_node:
            case ClassNodeDto():
                dto = MethodNodeDto(fqn=func_fqn, name=func_def.name)
                parent_node.contains(dto)
            case ModuleNodeDto():
                dto = FunctionNodeDto(fqn=func_fqn, name=func_def.name)
                parent_node.contains(dto)
        self._add_node(dto)
        return dto

    def _parse_ann_assign(
        self, ann_assign: AstAnnAssign, parent_node: ModuleNodeDto | ClassNodeDto
    ) -> None:
        target = ann_assign.target
        if not isinstance(target, AstName):
            return
        var_fqn = f"{parent_node.fqn}::{target.id}"
        dto = VariableNodeDto(fqn=var_fqn, name=target.id)
        parent_node.contains(dto)
        self._add_node(dto)

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
        parent_node.contains(dto)
        self._add_node(dto)

