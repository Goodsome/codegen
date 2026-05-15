from dataclasses import dataclass
from typing import override

from sqlalchemy.orm import Session, selectinload

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.infrastructure.persistence.mappers.component_mapper import (
    ComponentMapper,
)
from codegen.code_metadata.infrastructure.persistence.models.behavior_model import (
    BehaviorModel,
)
from codegen.code_metadata.infrastructure.persistence.models.component_model import (
    ComponentModel,
)

@dataclass
class SqlAlchemyComponentRepository(ComponentRepository):
    """
    Component 仓储的 SQLAlchemy 实现。
    负责管理 Component 聚合根的持久化生命周期，隔离基础设施层与领域层。
    """

    session: Session

    @override
    def _add(self, aggregate: Component) -> None:
        """
        新增一个 Component 聚合根到数据库。
        """
        # 通过 Mapper 将领域模型转换为 ORM 模型
        orm_model = ComponentMapper.to_orm(aggregate)
        self.session.add(orm_model)

    @override
    def _get(self, id: ComponentId) -> Component:
        """
        根据 ID 获取 Component 聚合根。如果找不到则抛出异常。
        """

        orm_model = self.session.get(
            ComponentModel,
            id.value,
            options=[
                selectinload(ComponentModel.attributes),
                selectinload(ComponentModel.behaviors).selectinload(
                    BehaviorModel.inputs
                ),
            ],
        )
        if orm_model is None:
            raise ValueError(f"Component with id {id.value} not found")

        return ComponentMapper.to_domain(orm_model)

    @override
    def _save(self, aggregate: Component) -> None:
        """
        更新现有的 Component 聚合根。
        """
        orm_model = ComponentMapper.to_orm(aggregate)

        self.session.merge(orm_model)

    @override
    def _delete(self, id: ComponentId) -> None:
        """
        删除 Component 聚合根及其所有下属实体。
        """
        model = self.session.get(ComponentModel, id.value)
        if model:
            self.session.delete(model)
            self.session.flush()
