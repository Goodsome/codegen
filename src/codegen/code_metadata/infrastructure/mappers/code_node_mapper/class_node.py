"""ClassNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations
from typing import Any

from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.value_objects.ast_expr import ast_expr_adapter
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.base_mapper import (
    BaseMapper,
)
from codegen.code_metadata.infrastructure.orm_models import ClassNodeModel


class ClassNodeMapper:
    """ClassNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: ClassNodeModel) -> ClassNode:
        decorator_list = [
            ast_expr_adapter.validate_python(decorator)
            for decorator in orm_model.decorator_list
        ]
        return ClassNode(
            fqn=orm_model.fqn,
            name=orm_model.name,
            description=orm_model.description,
            outbound_edges=BaseMapper.to_outbound_edge_dtos(orm_model),
            decorator_list=decorator_list
        )

    @classmethod
    def to_properties(cls, dto: ClassNode) -> dict[str, Any]:
        decorator_list = [
            ast_expr_adapter.dump_python(decorator, mode="json")
            for decorator in dto.decorator_list
        ]
        return {
            "decorator_list": decorator_list
        }