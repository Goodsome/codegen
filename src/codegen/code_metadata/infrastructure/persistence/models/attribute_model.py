from uuid import UUID
from typing import Any
from sqlalchemy import ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegen.shared.infrastructure.orm import BaseORM

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .component_model import ComponentModel
    from .behavior_model import BehaviorModel

class AttributeModel(BaseORM):
    __tablename__: str = "attributes"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    
    # 可选外键：取决于该属性是属于 Component 还是作为 Behavior 的输入
    component_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), 
        index=True, 
        nullable=True
    )
    behavior_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("behaviors.id", ondelete="CASCADE"), 
        index=True, 
        nullable=True
    )

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    
    # 值对象映射：TypeDef 存为递归嵌套的 JSONB
    type_def: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    
    value: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # 关联定义
    component: Mapped["ComponentModel | None"] = relationship(
        "ComponentModel", 
        back_populates="attributes",
        foreign_keys=[component_id]
    )
    behavior: Mapped["BehaviorModel | None"] = relationship(
        "BehaviorModel", 
        back_populates="inputs",
        foreign_keys=[behavior_id]
    )