"""VariableNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations
from typing import Any

from codegen.code_metadata.application.dtos.code_node_dto import VariableNodeDto
from codegen.code_metadata.domain.value_objects.ast_expr import ast_expr_adapter
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.base_mapper import (
    BaseMapper,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    VariableNodeModel,
)


class VariableNodeMapper:
    """VariableNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: VariableNodeModel) -> VariableNodeDto:
        annotation = (
            ast_expr_adapter.validate_python(orm_model.annotation)
            if orm_model.annotation
            else None
        )
        value = (
            ast_expr_adapter.validate_python(orm_model.value)
            if orm_model.value
            else None
        )
        return VariableNodeDto(
            fqn=orm_model.fqn,
            name=orm_model.name,
            annotation=annotation,
            value=value,
            outbound_edges=BaseMapper.to_outbound_edge_dtos(orm_model),
        )

    @classmethod
    def dto_to_upsert_dict(cls, dto: VariableNodeDto, sync_id: str) -> dict[str, Any]:
        annotation = (
            ast_expr_adapter.dump_python(dto.annotation, mode="json")
            if dto.annotation
            else None
        )
        value = (
            ast_expr_adapter.dump_python(dto.value, mode="json")
            if dto.value
            else None
        )
        properties = {
            "annotation": annotation,
            "value": value,
        }
        return {
            "fqn": dto.fqn,
            "kind": dto.kind.value,
            "name": dto.name,
            "properties": properties,
            "last_sync_id": sync_id,
        }