from typing import Annotated, Literal

from pydantic import Field
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.domain.value_objects.code_edge import OutboundEdge
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class BaseCodeNode(AggregateRoot[CodeNodeId]):
    fqn: str
    name: str

    outbound_edges: list[OutboundEdge]


class DirectoryNode(BaseCodeNode):
    kind: Literal[CodeNodeKind.DIRECTORY] = CodeNodeKind.DIRECTORY


class FileNode(BaseCodeNode):
    kind: Literal[CodeNodeKind.FILE] = CodeNodeKind.FILE


CodeNode = Annotated[
    DirectoryNode | FileNode,
    Field(discriminator="kind")
]