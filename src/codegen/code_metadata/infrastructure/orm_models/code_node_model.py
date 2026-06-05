from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.shared.infrastructure.orm_models.base import BaseORM

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
        CodeEdgeModel,
    )


class CodeNodeModel(BaseORM):
    """统一节点表"""

    __tablename__: str = "code_nodes"

    __mapper_args__: dict[str, str] = {
        "polymorphic_on": "kind",
    }

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    fqn: Mapped[str] = mapped_column(String(1024), unique=True, index=True)

    kind: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    properties: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )

    # Mark-and-Sweep 同步批次号：每次 ingest 生成一个，用于识别幽灵节点
    last_sync_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True,
    )

    outbound_edges: Mapped[list[CodeEdgeModel]] = relationship(
        "CodeEdgeModel",
        foreign_keys="[CodeEdgeModel.source_id]",
        back_populates="source_entity",
        cascade="all, delete-orphan",
        order_by="CodeEdgeModel.position.asc()"
    )

    inbound_edges: Mapped[list[CodeEdgeModel]] = relationship(
        "CodeEdgeModel",
        foreign_keys="[CodeEdgeModel.target_id]",
        back_populates="target_entity",
        viewonly=True,
    )


class DirectoryNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.DIRECTORY}


class FileNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.FILE}

class ModuleNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.MODULE}


class ClassNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.CLASS}


class FunctionNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.FUNCTION}


class MethodNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.METHOD}


class VariableNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.VARIABLE}


class ExternalNodeModel(CodeNodeModel):
    __mapper_args__: dict[str, str] = {"polymorphic_identity": CodeNodeKind.EXTERNAL}