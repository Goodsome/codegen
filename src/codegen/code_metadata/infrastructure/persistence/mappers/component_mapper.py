from typing import Any

# 导入你的领域模型 (Domain Models)
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.enums import ComponentType
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.behavior_id import BehaviorId
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.code_metadata.domain.value_objects.scenario import Scenario

# 导入上一步生成的 ORM 模型 (ORM Models)
from codegen.code_metadata.infrastructure.persistence.models.component_model import ComponentModel
from codegen.code_metadata.infrastructure.persistence.models.behavior_model import BehaviorModel
from codegen.code_metadata.infrastructure.persistence.models.attribute_model import AttributeModel


class ComponentMapper:
    """
    负责 Component 聚合根及其所有子实体、值对象在 Domain Model 和 ORM Model 之间的互相转换。
    """

    # ==========================================
    # ORM -> Domain (用于从数据库读取并重建聚合)
    # ==========================================
    
    @classmethod
    def to_domain(cls, orm_model: ComponentModel) -> Component:
        return Component(
            id=ComponentId.reconstitute(orm_model.id),  
            type=ComponentType(orm_model.type),
            name=orm_model.name,
            description=orm_model.description,
            context=orm_model.context,
            # 级联映射子实体
            attributes=[cls._attr_to_domain(attr) for attr in orm_model.attributes],
            behaviors=[cls._behavior_to_domain(beh) for beh in orm_model.behaviors]
        )

    @classmethod
    def _behavior_to_domain(cls, orm_model: BehaviorModel) -> Behavior:
        return Behavior(
            id=BehaviorId.reconstitute(orm_model.id),
            name=orm_model.name,
            description=orm_model.description,
            # 利用 Pydantic V2 的 model_validate 从 JSON dict 快速恢复嵌套值对象
            scenarios=[Scenario.model_validate(s) for s in orm_model.scenarios],
            inputs=[cls._attr_to_domain(attr) for attr in orm_model.inputs],
            output=TypeDef.model_validate(orm_model.output)
        )

    @classmethod
    def _attr_to_domain(cls, orm_model: AttributeModel) -> Attribute:
        return Attribute(
            id=AttributeId.reconstitute(orm_model.id),
            name=orm_model.name,
            description=orm_model.description,
            # 利用 Pydantic 将 JSON dict 转换为递归类型的 TypeDef
            type=TypeDef.model_validate(orm_model.type_def)
        )

    # ==========================================
    # Domain -> ORM (用于将聚合保存到数据库)
    # ==========================================

    @classmethod
    def to_orm(cls, domain_entity: Component) -> ComponentModel:
        # 注意：此处假设 domain_entity.id 能够直接提取为 UUID。
        # 如果你的 ComponentId 是一个复杂的类，请使用 domain_entity.id.value 提取底层 UUID
        component_id_val = domain_entity.id 
        
        return ComponentModel(
            id=component_id_val,
            type=domain_entity.type.value, # 枚举转字符串
            name=domain_entity.name,
            description=domain_entity.description,
            context=domain_entity.context,
            # 级联映射子实体，需要注入外键 component_id
            attributes=[
                cls._attr_to_orm(attr, component_id=component_id_val) 
                for attr in domain_entity.attributes
            ],
            behaviors=[
                cls._behavior_to_orm(beh, component_id=component_id_val) 
                for beh in domain_entity.behaviors
            ]
        )

    @classmethod
    def _behavior_to_orm(cls, domain_entity: Behavior, component_id: ComponentId) -> BehaviorModel:
        behavior_id_val = domain_entity.id
        
        return BehaviorModel(
            id=behavior_id_val,
            component_id=component_id,
            name=domain_entity.name,
            description=domain_entity.description,
            # Pydantic V2: model_dump(mode='json') 会自动将里面的所有类型(包括UUID, 枚举等)转为JSON兼容的基本类型
            scenarios=[s.model_dump(mode="json") for s in domain_entity.scenarios],
            output=domain_entity.output.model_dump(mode="json"),
            # Behavior 拥有的 inputs，注入外键 behavior_id
            inputs=[
                cls._attr_to_orm(attr, behavior_id=behavior_id_val) 
                for attr in domain_entity.inputs
            ]
        )

    @classmethod
    def _attr_to_orm(
        cls, 
        domain_entity: Attribute, 
        component_id: ComponentId | None = None, 
        behavior_id: BehaviorId | None = None
    ) -> AttributeModel:
        """
        动态处理双重归属权：
        如果作为 Component 的属性，component_id 有值；
        如果作为 Behavior 的输入参数，behavior_id 有值。
        """
        return AttributeModel(
            id=domain_entity.id,
            component_id=component_id,
            behavior_id=behavior_id,
            name=domain_entity.name,
            description=domain_entity.description,
            # 递归值对象转为 JSON dict
            type_def=domain_entity.type.model_dump(mode="json") 
        )