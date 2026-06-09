"""公共转换逻辑：边缘转换与详情 DTO 抽取。"""

from __future__ import annotations

from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.value_objects.code_edge import CodeEdge, create_edge
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
