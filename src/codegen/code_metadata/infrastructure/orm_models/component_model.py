from uuid import UUID
from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.orderinglist import ordering_list
from typing import Any

from codegen.shared.infrastructure.orm_models.base import BaseORM

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
    layer: Mapped[str] = mapped_column(String(50), index=True, server_default="unknown")
    
    bases: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)

    # 关联：一个组件拥有多个属性
    attributes: Mapped[list["AttributeModel"]] = relationship(
        "AttributeModel",
        back_populates="component",
        cascade="all, delete-orphan",
        foreign_keys="[AttributeModel.component_id]",
        order_by="AttributeModel.position",
        collection_class=ordering_list("position")
    )

    # 关联：一个组件拥有多个行为
    behaviors: Mapped[list["BehaviorModel"]] = relationship(
        "BehaviorModel",
        back_populates="component",
        cascade="all, delete-orphan",
        foreign_keys="[BehaviorModel.component_id]",
        order_by="BehaviorModel.position",
        collection_class=ordering_list("position")
    )