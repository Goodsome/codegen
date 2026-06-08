"""公共转换逻辑：边缘转换与详情 DTO 抽取。"""

from __future__ import annotations

from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDetailDto,
    InboundEdgeDto,
    OutboundEdgeDto,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.domain.value_objects.code_edge import OutboundEdge
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)


class BaseMapper:
    """所有节点类型 Mapper 的公共基类。"""

    # ------------------------------------------------------------------
    # ORM Edge → Domain Edge
    # ------------------------------------------------------------------

    @staticmethod
    def to_outbound_edge(edge_model: CodeEdgeModel) -> OutboundEdge:
        """将 CodeEdgeModel 转换为领域层的 OutboundEdge 值对象。"""
        return OutboundEdge(
            type=EdgeType(edge_model.type),
            target_id=CodeNodeId.reconstitute(edge_model.target_id),
        )

    # ------------------------------------------------------------------
    # Domain Edge → ORM Edge
    # ------------------------------------------------------------------

    @staticmethod
    def to_edge_model(source_id: CodeNodeId, edge: OutboundEdge) -> CodeEdgeModel:
        """将领域层的 OutboundEdge 转换为 CodeEdgeModel。"""
        return CodeEdgeModel(
            source_id=source_id.value,
            target_id=edge.target_id.value,
            type=edge.type.value,
        )

    # ------------------------------------------------------------------
    # ORM → OutboundEdgeDto 列表
    # ------------------------------------------------------------------

    @staticmethod
    def to_outbound_edge_dtos(orm_model: CodeNodeModel) -> list[OutboundEdgeDto]:
        """从 ORM 模型中提取出边 DTO 列表。"""
        return [
            OutboundEdgeDto(type=EdgeType(e.type), target_fqn=e.target_entity.fqn)
            for e in orm_model.outbound_edges
        ]

    # ------------------------------------------------------------------
    # ORM → Detail DTO（通用，所有节点类型共享）
    # ------------------------------------------------------------------

    @staticmethod
    def to_detail_dto(orm_model: CodeNodeModel) -> CodeNodeDetailDto:
        """ORM → 详情 DTO（含入边和出边）。所有节点类型通用。"""
        outbound_edges = [
            OutboundEdgeDto(type=EdgeType(e.type), target_fqn=e.target_entity.fqn)
            for e in orm_model.outbound_edges
        ]
        inbound_edges = [
            InboundEdgeDto(type=EdgeType(e.type), source_fqn=e.source_entity.fqn)
            for e in orm_model.inbound_edges
        ]
        return CodeNodeDetailDto(
            id=orm_model.id,
            fqn=orm_model.fqn,
            name=orm_model.name,
            kind=CodeNodeKind(orm_model.kind),
            description=orm_model.description,
            properties=orm_model.properties,
            outbound_edges=outbound_edges,
            inbound_edges=inbound_edges,
        )
