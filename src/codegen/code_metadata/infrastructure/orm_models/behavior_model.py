from uuid import UUID
from typing import Any
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegen.shared.infrastructure.orm_models.base import BaseORM

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .attribute_model import AttributeModel
    from .component_model import ClassComponentModel

class BehaviorModel(BaseORM):
    __tablename__: str = "behaviors"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    component_id: Mapped[UUID] = mapped_column(ForeignKey("components.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    scenarios: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    output: Mapped[dict[str, Any]] = mapped_column(JSONB)
    body: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)

    # 关联
    component: Mapped["ClassComponentModel"] = relationship(back_populates="behaviors")
    
    # 输入参数关联：Behavior 拥有的 inputs 也是 Attribute 实体
    inputs: Mapped[list["AttributeModel"]] = relationship(
        "AttributeModel",
        back_populates="behavior",
        cascade="all, delete-orphan",
        foreign_keys="[AttributeModel.behavior_id]"
    )