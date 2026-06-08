"""ModuleNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations

from codegen.code_metadata.application.dtos.code_node_dto import ModuleNodeDto
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.identifiers.code_node_id import CodeNodeId
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.base_mapper import (
    BaseMapper,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
    ModuleNodeModel,
)


class ModuleNodeMapper:
    """ModuleNode 专属的三向 Mapper。"""

    @classmethod
    def to_domain(cls, orm_model: CodeNodeModel) -> ModuleNode:
        assert isinstance(orm_model, ModuleNodeModel)
        return ModuleNode(
            id=CodeNodeId.reconstitute(orm_model.id),
            fqn=orm_model.fqn,
            name=orm_model.name,
            is_package=orm_model.is_package,
            outbound_edges=[BaseMapper.to_outbound_edge(e) for e in orm_model.outbound_edges],
        )

    @classmethod
    def to_dto(cls, orm_model: CodeNodeModel) -> ModuleNodeDto:
        assert isinstance(orm_model, ModuleNodeModel)
        return ModuleNodeDto(
            fqn=orm_model.fqn,
            name=orm_model.name,
            description=orm_model.description,
            is_package=orm_model.is_package,
            outbound_edges=BaseMapper.to_outbound_edge_dtos(orm_model),
        )

    @classmethod
    def to_orm(cls, domain_entity: ModuleNode) -> ModuleNodeModel:
        model = ModuleNodeModel(
            id=domain_entity.id.value,
            fqn=domain_entity.fqn,
            name=domain_entity.name,
        )
        model.is_package = domain_entity.is_package
        model.outbound_edges = [
            BaseMapper.to_edge_model(domain_entity.id, edge)
            for edge in domain_entity.outbound_edges
        ]
        return model
