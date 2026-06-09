"""ClassNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations

from codegen.code_metadata.application.dtos.code_node_dto import ClassNodeDto
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.base_mapper import (
    BaseMapper,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)


class ClassNodeMapper:
    """ClassNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: CodeNodeModel) -> ClassNodeDto:
        return ClassNodeDto(
            fqn=orm_model.fqn,
            name=orm_model.name,
            description=orm_model.description,
            outbound_edges=BaseMapper.to_outbound_edge_dtos(orm_model),
        )
