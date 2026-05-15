from uuid import UUID
from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegen.shared.infrastructure.orm import BaseORM

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .attribute_model import AttributeModel
    from .behavior_model import BehaviorModel

class ComponentModel(BaseORM):
    __tablename__: str = "components"

    __table_args__ = (
        UniqueConstraint("context", "name", name="uq_component_context_name"),
    )
    

    id: Mapped[UUID] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    context: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    # 关联：一个组件拥有多个属性
    attributes: Mapped[list["AttributeModel"]] = relationship(
        "AttributeModel",
        back_populates="component",
        cascade="all, delete-orphan",
        foreign_keys="[AttributeModel.component_id]"
    )

    # 关联：一个组件拥有多个行为
    behaviors: Mapped[list["BehaviorModel"]] = relationship(
        "BehaviorModel",
        back_populates="component",
        cascade="all, delete-orphan"
    )