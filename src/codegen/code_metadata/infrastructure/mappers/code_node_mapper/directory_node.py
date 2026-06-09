"""DirectoryNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations

from typing import Any

from codegen.code_metadata.domain.aggregates.code_node import DirectoryNode
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.base_mapper import (
    BaseMapper,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    DirectoryNodeModel,
)


class DirectoryNodeMapper:
    """DirectoryNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: DirectoryNodeModel) -> DirectoryNode:
        return DirectoryNode(
            fqn=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=BaseMapper.to_outbound_edge_dtos(orm_model),
        )

    @classmethod
    def to_properties(cls, dto: DirectoryNode) -> dict[str, Any]:
        return {}
