"""MethodNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations

from codegen.code_metadata.application.dtos.code_node_dto import MethodNodeDto
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.base_mapper import (
    BaseMapper,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
    MethodNodeModel,
)


class MethodNodeMapper:
    """MethodNode 专属的三向 Mapper。"""

    @classmethod
    def to_domain(cls, orm_model: CodeNodeModel) -> MethodNode:
        assert isinstance(orm_model, MethodNodeModel)
        return MethodNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=[BaseMapper.to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def to_dto(cls, orm_model: CodeNodeModel) -> MethodNodeDto:
        return MethodNodeDto(
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=BaseMapper.to_outbound_edge_dtos(orm_model),
        )

    @classmethod
    def to_orm(cls, domain_entity: MethodNode) -> MethodNodeModel:
        model = MethodNodeModel(
            id=domain_entity.id.value,
            fqn=domain_entity.fqn,
            name=domain_entity.name,
        )
        model.outbound_edges = [
            BaseMapper.to_edge_model(domain_entity.id, edge)
            for edge in domain_entity.outbound_edges
        ]
        return model
