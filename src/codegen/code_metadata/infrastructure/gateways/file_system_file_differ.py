from dataclasses import dataclass
from pathlib import Path
from typing import override

from codegen.code_dom.application.queries.get_code_document_diff import (
    GetCodeDocumentDiffHandler,
    GetCodeDocumentDiffQuery,
)
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_metadata.application.dtos.code_node_dto import (
    ClassNodeDto,
    CodeNodeDto,
    FunctionNodeDto,
    MethodNodeDto,
    ModuleNodeDto,
    OutboundEdgeDto,
    VariableNodeDto,
)
from codegen.code_metadata.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.application.ports.file_differ import FileDiffer
from codegen.code_metadata.application.registry.node_registry import NodeRegistry
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects import (
    AstAnnAssign,
    AstArguments,
    AstAssign,
    AstFunctionDef,
    AstName,
    AstPass,
    AstStmt,
)
from codegen.code_metadata.domain.value_objects.arg import Arg
from codegen.code_metadata.domain.value_objects.ast_class_def import AstClassDef


@dataclass
class FileSystemFileDiffer(FileDiffer):
    handler: GetCodeDocumentDiffHandler

    @override
    def get_diff_metric(
        self, module: ModuleNodeDto, node_registry: NodeRegistry
    ) -> FileMetrics:
        code_document = module_node_dto_to_code_document(module, node_registry)
        query = GetCodeDocumentDiffQuery(code_document=code_document)
        file_metrics = self.handler.execute(query=query)
        return file_metrics


def module_node_dto_to_code_document(
    module: ModuleNodeDto, node_registry: NodeRegistry
) -> CodeDocument:
    physical_path = Path("src") / module.fqn.replace(".", "/")
    if module.is_package:
        physical_path = physical_path / "__init__.py"

    body = collect_body_from_outbound_edges(module.outbound_edges, node_registry)

    return CodeDocument(
        physical_path=physical_path,
        body=body,
        description=module.description,
    )


def node_to_ast(node: CodeNodeDto, node_registry: NodeRegistry) -> AstStmt:
    match node:
        case ClassNodeDto():
            return class_node_dto_to_ast_class_def(node, node_registry)
        case MethodNodeDto() | FunctionNodeDto():
            return method_node_dto_to_ast(node, node_registry)
        case VariableNodeDto():
            return variable_node_dto_to_ast(node, node_registry)
        case _:
            raise NotImplementedError(f"{node}=")


def class_node_dto_to_ast_class_def(
    class_node: ClassNodeDto, node_registry: NodeRegistry
) -> AstClassDef:
    body = collect_body_from_outbound_edges(class_node.outbound_edges, node_registry)

    return AstClassDef(
        name=class_node.name,
        description=class_node.description,
        bases=[],
        keywords=[],
        body=body,
        decorator_list=[],
    )


def method_node_dto_to_ast(
    method_node: MethodNodeDto | FunctionNodeDto,
    node_registry: NodeRegistry,
) -> AstFunctionDef:
    arguments = collect_arguments_from_outbound_edges(
        method_node.outbound_edges, node_registry
    )
    body: list[AstStmt] = []
    if not body:
        body = [AstPass()]
    return AstFunctionDef(
        name=method_node.name,
        body=body,
        decorator_list=[],
        lineno=0,
        arguments=arguments,
    )


def variable_node_dto_to_ast(
    variable_node: VariableNodeDto, node_registry: NodeRegistry
) -> AstAssign | AstAnnAssign:
    target = AstName(id=variable_node.name)
    if variable_node.annotation:
        return AstAnnAssign(
            target=target,
            annotation=variable_node.annotation,
            value=None,
        )
    return AstAssign(targets=[target], value=variable_node.value)


def collect_body_from_outbound_edges(
    edges: list[OutboundEdgeDto], node_registry: NodeRegistry
) -> list[AstStmt]:
    body: list[AstStmt] = []
    for edge in edges:
        if edge.type not in [EdgeType.CONTAINS, EdgeType.IMPORTS]:
            continue
        target_node = node_registry.get_node(edge.target_fqn)
        ast_stmt = node_to_ast(target_node, node_registry)
        body.append(ast_stmt)

    return body


def collect_arguments_from_outbound_edges(
    edges: list[OutboundEdgeDto], node_registry: NodeRegistry
) -> list[AstAssign | AstAnnAssign]:
    arguments: list[AstAssign | AstAnnAssign] = []
    for edge in edges:
        if edge.type is not EdgeType.CONTAINS:
            continue
        target_node = node_registry.get_node(edge.target_fqn)
        if not isinstance(target_node, VariableNodeDto):
            continue
        ast_arg = variable_node_dto_to_ast(target_node, node_registry)
        arguments.append(ast_arg)

    return arguments
