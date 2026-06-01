from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.shared.domain.core import ValueObject


class CodeEdge(ValueObject):
    type: EdgeType


class OutboundEdge(CodeEdge):
    target_id: CodeNodeId


class InboundEdge(CodeEdge):
    source_id: CodeNodeId
    
