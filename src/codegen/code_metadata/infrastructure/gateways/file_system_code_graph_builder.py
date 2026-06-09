from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_dom.application.queries.get_project_documents import (
    GetProjectDocumentsHandler,
    GetProjectDocumentsQuery,
)
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.ports.code_graph_builder import CodeGraphBuilder
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.aggregates.code_node import (
    ClassNode,
    CodeNode,
    FunctionNode,
    MethodNode,
    ModuleNode,
    VariableNode,
)
from codegen.code_metadata.domain.factories.fqn_factory import FqnFactory
from codegen.code_metadata.domain.value_objects import (
    AstConstant,
    AstExpr,
    AstExprStmt,
    AstIf,
    AstImport,
    AstImportFrom,
    AstPass,
)
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef
from codegen.code_metadata.domain.value_objects.ast_function_def import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from codegen.code_metadata.infrastructure.gateways.module_build_context import (
    ModuleBuildContext,
)


@dataclass
class FileSystemCodeGraphBuilder(CodeGraphBuilder):
    """从文件系统构建 CodeNode 图的实现。

    通过 GetProjectDocumentsHandler 获取项目文档列表，
    再从文档路径派生目录树结构，同步完成节点构造和 CONTAINS 边的建立。
    """

    get_project_documents: GetProjectDocumentsHandler

    @override
    def build(self, fqn_prefix: str) -> list[CodeNode]:
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

    def build_nodes(self, code_documents: list[CodeDocument]) -> list[CodeNode]:
        for doc in code_documents:
            self._build_module_node(doc)
            
        self._build_edges(code_documents=code_documents)

        return self.node_registery.nodes

    def _build_edges(self, code_documents: list[CodeDocument]) -> None:
        for code_document in code_documents:
            module_fqn = self.fqn_factory.build_module_fqn(code_document.physical_path)
            module = self.node_registery.get_node(module_fqn)
            assert isinstance(module, ModuleNode)
            module_builder = ModuleBuildContext(
                module, code_document, self.node_registery
            )
            module_builder.build()

    def _add_node(self, dto: CodeNode) -> None:
        self.node_registery.add_node(dto)

    def _build_module_node(
        self, code_document: CodeDocument
    ) -> ModuleNode:
        path = code_document.physical_path
        module_fqn = self.fqn_factory.build_module_fqn(path)
        module_node = ModuleNode(
            fqn=module_fqn,
            name=module_fqn.rsplit(".", maxsplit=1)[-1],
            is_package=path.name == "__init__.py",
            description=code_document.description,
        )
        self._add_node(module_node)

        for stmt in code_document.body:
            self._parse_stmt(stmt, module_node)

        return module_node

    def _parse_stmt(self, stmt: AstStmt, parent_node: ModuleNode | ClassNode) -> None:
        match stmt:
            case AstClassDef():
                assert isinstance(parent_node, ModuleNode)
                self._parse_class_def(stmt, parent_node)
            case AstFunctionDef():
                self._parse_function_def(stmt, parent_node)
            case AstAssign() | AstAnnAssign():
                self._parse_assign(stmt, parent_node)
            case (
                AstImport() | AstImportFrom() | AstIf(test=AstName(id="TYPE_CHECKING"))
            ):
                pass
            case AstExprStmt(value=AstConstant()):
                pass
            case AstExprStmt():
                self._parse_expr(stmt, parent_node)
            case AstPass():
                pass
            case _:
                raise NotImplementedError(
                    f"Unsupported statement: {stmt=} in {parent_node.fqn=}"
                )

    def _parse_expr(self, stmt: AstExprStmt, node: ModuleNode | ClassNode):
        if isinstance(node, ClassNode):
            raise NotImplementedError(f"{stmt=}, {node=}")
        node.exprs.append(stmt.value)

    def _parse_class_def(
        self, class_def: AstClassDef, module_node: ModuleNode
    ) -> ClassNode:
        class_fqn = f"{module_node.fqn}::{class_def.name}"
        node = ClassNode(
            fqn=class_fqn,
            name=class_def.name,
            description=class_def.description,
            decorator_list=class_def.decorator_list,
            bases=class_def.bases,
        )
        module_node.contains(node)
        for stmt in class_def.body:
            self._parse_stmt(stmt, node)

        self._add_node(node)
        return node

    def _parse_function_def(
        self, func_def: AstFunctionDef, parent_node: ModuleNode | ClassNode
    ) -> FunctionNode | MethodNode:
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
            case ClassNode():
                func_node = MethodNode(
                    fqn=func_fqn,
                    name=func_def.name,
                    decorator_list=func_def.decorator_list,
                    returns=func_def.returns,
                    body=func_def.body,
                )
                parent_node.contains(func_node)
            case ModuleNode():
                func_node = FunctionNode(
                    fqn=func_fqn,
                    name=func_def.name,
                    decorator_list=func_def.decorator_list,
                    returns=func_def.returns,
                    body=func_def.body,
                )
                parent_node.contains(func_node)
        self._add_node(func_node)

        for arg in func_def.arguments:
            self._parse_assign(arg, func_node)

        return func_node

    def _parse_assign(
        self,
        assign: AstAssign | AstAnnAssign,
        parent_node: ModuleNode | ClassNode | MethodNode | FunctionNode,
    ) -> None:
        target = assign.target
        if not isinstance(target, AstName):
            return
        self._create_variable_node(
            name=target.id,
            parent_node=parent_node,
            annotation=assign.annotation,
            value=assign.value,
        )

    def _create_variable_node(
        self,
        name: str,
        parent_node: ModuleNode | ClassNode | FunctionNode | MethodNode,
        annotation: AstExpr | None = None,
        value: AstExpr | None = None,
    ) -> VariableNode:
        var_fqn = f"{parent_node.fqn}::{name}"
        node = VariableNode(
            fqn=var_fqn,
            name=name,
            annotation=annotation,
            value=value,
        )
        parent_node.contains(node)
        self._add_node(node)

        return node
