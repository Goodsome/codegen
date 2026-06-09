from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_dom.application.queries.get_code_document_diff import (
    GetCodeDocumentDiffHandler,
    GetCodeDocumentDiffQuery,
)
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.domain.aggregates.code_node import (
    ClassNode,
    CodeNode,
    FunctionNode,
    MethodNode,
    ModuleNode,
    VariableNode,
)
from codegen.code_metadata.domain.value_objects.code_edge import CodeEdge, ContainsEdge, ImportsEdge, InheritsEdge
from codegen.code_metadata.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.application.ports.file_differ import FileDiffer
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects import (
    AstAlias,
    AstAnnAssign,
    AstAssign,
    AstExpr,
    AstFunctionDef,
    AstImport,
    AstImportFrom,
    AstName,
    AstPass,
    AstStmt,
)
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef


@dataclass
class FileSystemFileDiffer(FileDiffer):
    handler: GetCodeDocumentDiffHandler

    @override
    def get_diff_metric(
        self, module: ModuleNode, node_registry: NodeRegistry
    ) -> FileMetrics:
        code_document = module_node_dto_to_code_document(module, node_registry)
        query = GetCodeDocumentDiffQuery(code_document=code_document)
        file_metrics = self.handler.execute(query=query)
        return file_metrics


def module_node_dto_to_code_document(
    module: ModuleNode, node_registry: NodeRegistry
) -> CodeDocument:
    physical_path = Path("src") / module.fqn.replace(".", "/")
    if module.is_package:
        physical_path = physical_path / "__init__.py"

    imports: list[AstStmt] = []
    body: list[AstStmt] = []
    
    for edge in module.outbound_edges:
        if edge.kind == EdgeType.IMPORTS:
            imports.append(edge_to_ast_stmt(edge, node_registry))
        else:
            body.append(edge_to_ast_stmt(edge, node_registry))

    return CodeDocument(
        physical_path=physical_path,
        body=imports + body,
        description=module.description,
    )

def edge_to_ast_stmt(edge: CodeEdge, node_registry: NodeRegistry) -> AstStmt:
    match edge:
        case ImportsEdge():
            return imports_edge_to_ast(edge, node_registry)
        case ContainsEdge():
            return contains_edge_to_ast(edge, node_registry)
        case _:
            raise NotImplementedError(f"{edge=}")


def node_to_ast_stmt(node: CodeNode, node_registry: NodeRegistry) -> AstStmt:
    match node:
        case ClassNode():
            return class_node_dto_to_ast_class_def(node, node_registry)
        case MethodNode() | FunctionNode():
            return method_node_dto_to_ast(node, node_registry)
        case VariableNode():
            return variable_node_dto_to_ast(node, node_registry)
        case _:
            raise NotImplementedError(f"{node}=")

def edge_to_ast_expr(edge: CodeEdge, node_registry: NodeRegistry) -> AstExpr:
    match edge:
        case InheritsEdge():
            return inherits_edge_to_ast_name(edge, node_registry)
        case _:
            raise NotImplementedError(f"{edge=}")

def class_node_dto_to_ast_class_def(
    class_node: ClassNode, node_registry: NodeRegistry
) -> AstClassDef:
    bases: list[AstExpr] = []
    body: list[AstStmt] = []
    for edge in class_node.outbound_edges:
        match edge:
            case InheritsEdge():
                ast_expr = edge_to_ast_expr(edge, node_registry)
                bases.append(ast_expr)
            case _:
                body.append(edge_to_ast_stmt(edge, node_registry))

    return AstClassDef(
        name=class_node.name,
        description=class_node.description,
        bases=bases,
        keywords=[],
        body=body,
        decorator_list=class_node.decorator_list,
    )


def method_node_dto_to_ast(
    method_node: MethodNode | FunctionNode,
    node_registry: NodeRegistry,
) -> AstFunctionDef:
    arguments = collect_arguments_from_outbound_edges(
        method_node.outbound_edges, node_registry
    )
    return AstFunctionDef(
        name=method_node.name,
        body=method_node.body,
        decorator_list=method_node.decorator_list,
        lineno=0,
        arguments=arguments,
        returns=method_node.returns,
    )


def variable_node_dto_to_ast(
    variable_node: VariableNode, node_registry: NodeRegistry
) -> AstAssign | AstAnnAssign:
    target = AstName(id=variable_node.name)
    if variable_node.annotation:
        return AstAnnAssign(
            target=target,
            annotation=variable_node.annotation,
            value=variable_node.value,
        )
    return AstAssign(targets=[target], value=variable_node.value)

def contains_edge_to_ast(edge: ContainsEdge, node_registry: NodeRegistry) -> AstStmt:
    target_node = node_registry.get_node(edge.fqn)
    ast_stmt = node_to_ast_stmt(target_node, node_registry)
    return ast_stmt

def inherits_edge_to_ast_name(edge: InheritsEdge, node_registry: NodeRegistry) -> AstName:
    if "::" in edge.fqn:
        name = edge.fqn.rsplit("::", 1)[-1]
    else:
        name = edge.fqn.rsplit(".", 1)[-1]
    return AstName(
        id=name,
    )

def imports_edge_to_ast(
    edge: ImportsEdge, node_registry: NodeRegistry
) -> AstImport | AstImportFrom:
    if "::" in edge.fqn:
        module, name = edge.fqn.rsplit("::", 1)
        return AstImportFrom(module=module, names=[AstAlias(name=name, asname=None)])
    elif "." in edge.fqn:
        module, name = edge.fqn.rsplit(".", 1)
        return AstImportFrom(module=module, names=[AstAlias(name=name, asname=None)])
    else:
        return AstImport(names=[AstAlias(name=edge.fqn, asname=None)])


def collect_arguments_from_outbound_edges(
    edges: list[CodeEdge], node_registry: NodeRegistry
) -> list[AstAssign | AstAnnAssign]:
    arguments: list[AstAssign | AstAnnAssign] = []
    for edge in edges:
        if edge.kind is not EdgeType.CONTAINS:
            continue
        target_node = node_registry.get_node(edge.fqn)
        if not isinstance(target_node, VariableNode):
            continue
        ast_arg = variable_node_dto_to_ast(target_node, node_registry)
        arguments.append(ast_arg)

    return arguments
