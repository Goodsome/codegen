from typing import Annotated, Literal

from pydantic import Field
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.domain.value_objects.code_edge import OutboundEdge
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class BaseCodeNode(AggregateRoot[CodeNodeId]):
    fqn: str
    name: str

    outbound_edges: list[OutboundEdge]

    def has_edge_to(self, target_id: CodeNodeId) -> bool:
        """检查是否已存在指向目标节点的边。"""
        return any(e.target_id == target_id for e in self.outbound_edges)

    def add_contains_edge(self, target_id: CodeNodeId) -> None:
        """添加 CONTAINS 边（幂等：已存在则跳过）。"""
        if not self.has_edge_to(target_id):
            self.outbound_edges.append(
                OutboundEdge(type=EdgeType.CONTAINS, target_id=target_id)
            )


class DirectoryNode(BaseCodeNode):
    kind: Literal[CodeNodeKind.DIRECTORY] = CodeNodeKind.DIRECTORY


class FileNode(BaseCodeNode):
    kind: Literal[CodeNodeKind.FILE] = CodeNodeKind.FILE

class ModuleNode(BaseCodeNode):
    kind: Literal[CodeNodeKind.MODULE] = CodeNodeKind.MODULE

class ClassNode(BaseCodeNode):
    kind: Literal[CodeNodeKind.CLASS] = CodeNodeKind.CLASS


class FunctionNode(BaseCodeNode):
    kind: Literal[CodeNodeKind.FUNCTION] = CodeNodeKind.FUNCTION


CodeNode = Annotated[
    DirectoryNode | FileNode | ModuleNode | ClassNode | FunctionNode,
    Field(discriminator="kind")
]