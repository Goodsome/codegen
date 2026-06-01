from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Integer, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegen.shared.infrastructure.orm_models.base import BaseORM

if TYPE_CHECKING:
    from .code_node_model import CodeNodeModel

class CodeEdgeModel(BaseORM):
    """
    统一的关联实体表（图谱边表）
    """
    __tablename__: str = "code_edges"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("code_nodes.id", ondelete="CASCADE"), 
        index=True
    )
    target_id: Mapped[UUID] = mapped_column(
        ForeignKey("code_nodes.id", ondelete="CASCADE"), 
        index=True
    )
    
    type: Mapped[str] = mapped_column(String(50), index=True)
    
    # === 2. 边属性 (Edge Properties) ===
    # AST 节点的物理顺序，解决顺序丢失陷阱
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    metadata_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, server_default="{}")

    source_entity: Mapped[CodeNodeModel] = relationship("CodeNodeModel", foreign_keys=[source_id])
    target_entity: Mapped[CodeNodeModel] = relationship("CodeNodeModel", foreign_keys=[target_id])

    __table_args__ = (
        # 联合索引，加速 "查询某个节点的所有下游" 或 "查询某个节点的所有上游"
        Index("ix_rel_source_type", "source_id", "type"),
        Index("ix_rel_target_type", "target_id", "type"),
        
        # 幂等性保证：两点之间，同一种关系只能有一条（防重复插入）
        # 如果方法A两次调用了方法B，应该更新 metadata_payload 里的 call_count，而不是插入两条一模一样的边
        UniqueConstraint("source_id", "target_id", "type", name="uq_entity_edge"),
    )