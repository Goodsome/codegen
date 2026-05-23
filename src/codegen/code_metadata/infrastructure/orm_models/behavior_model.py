from uuid import UUID
from typing import Any
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from codegen.shared.infrastructure.orm_models.base import BaseORM

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .attribute_model import AttributeModel
    from .component_model import ComponentModel

class BehaviorModel(BaseORM):
    __tablename__: str = "behaviors"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    component_id: Mapped[UUID] = mapped_column(ForeignKey("components.id", ondelete="CASCADE"), index=True)
    
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    
    # 值对象映射：Scenario 列表存为 JSONB 数组
    # 结构示例: [{"name": "...", "steps": [{"type": "Given", "text": "..."}]}]
    scenarios: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    
    # 值对象映射：TypeDef 存为嵌套 JSONB 对象
    # 结构示例: {"origin": "...", "args": [...]}
    output: Mapped[dict[str, Any]] = mapped_column(JSONB)

    # 关联
    component: Mapped["ComponentModel"] = relationship(back_populates="behaviors")
    
    # 输入参数关联：Behavior 拥有的 inputs 也是 Attribute 实体
    inputs: Mapped[list["AttributeModel"]] = relationship(
        "AttributeModel",
        back_populates="behavior",
        cascade="all, delete-orphan",
        foreign_keys="[AttributeModel.behavior_id]"
    )