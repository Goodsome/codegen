"""ModuleNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations

from typing import Any

from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper import (
    to_outbound_edges,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
    ModuleNodeModel,
)


class ModuleNodeMapper:
    """ModuleNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: CodeNodeModel) -> ModuleNode:
        assert isinstance(orm_model, ModuleNodeModel)
        return ModuleNode(
            fqn=orm_model.fqn,
            name=orm_model.name,
            description=orm_model.description,
            is_package=orm_model.is_package,
            outbound_edges=to_outbound_edges(orm_model.outbound_edges),
        )

    @classmethod
    def to_properties(cls, dto: ModuleNode) -> dict[str, Any]:
        return {"is_package": dto.is_package}
