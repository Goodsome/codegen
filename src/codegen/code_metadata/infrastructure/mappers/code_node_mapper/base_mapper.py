"""公共转换逻辑：边缘转换与详情 DTO 抽取。"""

from __future__ import annotations

from codegen.code_metadata.application.dtos.code_node_dto import (
    CodeNodeDetailDto,
)
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.value_objects.edge import CodeEdge, create_edge
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)


class BaseMapper:
    """所有节点类型 Mapper 的公共基类。"""

    # ------------------------------------------------------------------
    # ORM → Edge 列表
    # ------------------------------------------------------------------

    @staticmethod
    def to_outbound_edge_dtos(orm_model: CodeNodeModel) -> list[CodeEdge]:
        """从 ORM 模型中提取出边列表。"""
        return [
            create_edge(EdgeType(e.type), e.target_entity.fqn, EdgeDirection.OUT)
            for e in orm_model.outbound_edges
        ]

    # ------------------------------------------------------------------
    # ORM → Detail DTO（通用，所有节点类型共享）
    # ------------------------------------------------------------------

    @staticmethod
    def to_detail_dto(orm_model: CodeNodeModel) -> CodeNodeDetailDto:
        """ORM → 详情 DTO（含入边和出边）。所有节点类型通用。"""
        outbound_edges = [
            create_edge(EdgeType(e.type), e.target_entity.fqn, EdgeDirection.OUT)
            for e in orm_model.outbound_edges
        ]
        inbound_edges = [
            create_edge(EdgeType(e.type), e.source_entity.fqn, EdgeDirection.IN)
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
