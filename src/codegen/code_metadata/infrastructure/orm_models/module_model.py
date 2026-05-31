from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegen.code_metadata.infrastructure.orm_models.component_v2_model import ComponentV2Model
from codegen.shared.infrastructure.orm_models.base import BaseORM


class ModuleModel(BaseORM):
    __tablename__: str = "modules"

    __mapper_args__ = {
        "polymorphic_on": "kind",
    }

    id: Mapped[UUID] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1024), unique=True)

    # FileModule / DirectoryModule 共用
    dir_module_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("modules.id", ondelete="SET NULL"),
        nullable=True,
    )

    # FileModule / ExternalModule 共享：通过 module_id 反查 components
    components: Mapped[list[ComponentV2Model]] = relationship(
        "ComponentV2Model",
        foreign_keys="[ComponentV2Model.module_id]",
        cascade="all, delete-orphan",
    )


class FileModuleModel(ModuleModel):
    __mapper_args__ = {
        "polymorphic_identity": "file",
    }

    dependencies: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, server_default="[]")


class DirectoryModuleModel(ModuleModel):
    __mapper_args__ = {
        "polymorphic_identity": "directory",
    }

    public_component_ids: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=list, server_default="[]",
    )
    sub_module_ids: Mapped[list[UUID]] = mapped_column(
        JSONB, default=list, server_default="[]",
    )


class ExternalModuleModel(ModuleModel):
    __mapper_args__ = {
        "polymorphic_identity": "external",
    }
