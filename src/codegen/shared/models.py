"""
实体、值对象、聚合根基类

提供 DDD 战术设计的核心构建块：
- Entity: 具有唯一标识的领域对象
- ValueObject: 不可变的值对象
- AggregateRoot: 聚合根，管理领域事件
"""

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from codegen.shared.events import DomainEvent


class Entity(BaseModel):
    """实体基类

    特征：
    1. 具有唯一标识（ID）
    2. 相等性基于 ID 判断
    3. 可变（但应通过行为方法修改）
    4. 使用 UTC 时区记录时间
    """

    model_config = ConfigDict(extra="forbid")

    # def __eq__(self, other: Any) -> bool:
    #     """实体相等性基于 ID 判断"""
    #     if not isinstance(other, Entity):
    #         return False
    #     return self.id == other.id

    # def __hash__(self) -> int:
    #     return hash(self.id)


class ValueObject(BaseModel):
    """值对象基类

    特征：
    1. 不可变（frozen=True）
    2. 相等性基于所有属性值
    3. 无唯一标识
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class AggregateRoot(Entity):
    """聚合根基类

    特征：
    1. 继承 Entity 的所有特性
    2. 管理领域事件的发布和收集
    3. 确保聚合边界内的一致性
    """

    _domain_events: list["DomainEvent"] = PrivateAttr(default_factory=list)

    def add_domain_event(self, event: "DomainEvent") -> None:  # noqa: F821
        """添加领域事件

        Args:
            event: 要添加的领域事件实例

        Raises:
            TypeError: 如果 event 不是 DomainEvent 的实例
        """
        # 延迟导入避免循环依赖
        from .events import DomainEvent

        if not isinstance(event, DomainEvent):
            raise TypeError(f"Expected DomainEvent, got {type(event).__name__}")

        self._domain_events.append(event)

    def collect_events(self) -> list["DomainEvent"]:  # noqa: F821
        """收集并清空领域事件

        Returns:
            收集到的所有领域事件列表（副本）
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def clear_events(self) -> None:
        """清空领域事件"""
        self._domain_events.clear()

    def has_events(self) -> bool:
        """检查是否有未处理的领域事件

        Returns:
            如果有事件返回 True，否则返回 False
        """
        return len(self._domain_events) > 0
