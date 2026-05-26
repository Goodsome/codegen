from codegen.code_metadata.application.dtos.component_dto import ComponentDto
from codegen.code_metadata.domain.aggregates.component import ClassComponent
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums import ArchitectureLayer, ComponentType
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.behavior_id import BehaviorId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.ast_stmt import ast_stmt_adapter
from codegen.code_metadata.domain.value_objects.expr_def import expr_def_adapter
from codegen.code_metadata.domain.value_objects.scenario import Scenario
from codegen.code_metadata.domain.value_objects.type_def import TypeDef
from codegen.code_metadata.infrastructure.orm_models.attribute_model import (
    AttributeModel,
)
from codegen.code_metadata.infrastructure.orm_models.behavior_model import (
    BehaviorModel,
)
from codegen.code_metadata.infrastructure.orm_models.component_model import (
    ComponentModel,
)


class ComponentMapper:
    """
    负责 Component 聚合根及其所有子实体、值对象在 Domain Model 和 ORM Model 之间的互相转换。
    """

    @classmethod
    def to_dto(cls, orm_model: ComponentModel) -> ComponentDto:
        return ComponentDto(
            id=str(orm_model.id),
            kind=orm_model.kind,
            type=orm_model.type,
            name=orm_model.name,
            description=orm_model.description,
            context=orm_model.context,
            layer=orm_model.layer,
            bases=orm_model.bases,
        )

    # ==========================================
    # ORM -> Domain (用于从数据库读取并重建聚合)
    # ==========================================

    @classmethod
    def to_domain(cls, orm_model: ComponentModel) -> ClassComponent:
        return ClassComponent(
            id=ComponentId.reconstitute(orm_model.id),
            type=ComponentType(orm_model.type),
            name=orm_model.name,
            description=orm_model.description,
            context=orm_model.context,
            layer=ArchitectureLayer(orm_model.layer),
            bases=[TypeDef.model_validate(t) for t in orm_model.bases],
            # 级联映射子实体
            attributes=[cls._attr_to_domain(attr) for attr in orm_model.attributes],
            behaviors=[cls._behavior_to_domain(beh) for beh in orm_model.behaviors],
        )

    @classmethod
    def _behavior_to_domain(cls, orm_model: BehaviorModel) -> Behavior:
        return Behavior(
            id=BehaviorId.reconstitute(orm_model.id),
            name=orm_model.name,
            description=orm_model.description,
            scenarios=[Scenario.model_validate(s) for s in orm_model.scenarios],
            inputs=[cls._attr_to_domain(attr) for attr in orm_model.inputs],
            output=TypeDef.model_validate(orm_model.output),
            body=[ast_stmt_adapter.validate_python(s) for s in orm_model.body],
        )

    @classmethod
    def _attr_to_domain(cls, orm_model: AttributeModel) -> Attribute:
        value = (
            expr_def_adapter.validate_python(orm_model.value)
            if orm_model.value
            else None
        )
        _type = (
            TypeDef.model_validate(orm_model.type_def)
            if orm_model.type_def
            else None
        )
        return Attribute(
            id=AttributeId.reconstitute(orm_model.id),
            name=orm_model.name,
            description=orm_model.description,
            type=_type,
            value=value,
        )

    # ==========================================
    # Domain -> ORM (用于将聚合保存到数据库)
    # ==========================================

    @classmethod
    def to_orm(cls, domain_entity: ClassComponent) -> ComponentModel:
        # 注意：此处假设 domain_entity.id 能够直接提取为 UUID。
        # 如果你的 ComponentId 是一个复杂的类，请使用 domain_entity.id.value 提取底层 UUID
        component_id_val = domain_entity.id

        return ComponentModel(
            id=component_id_val.value,
            kind=domain_entity.kind.value,
            type=domain_entity.type.value,  # 枚举转字符串
            name=domain_entity.name,
            description=domain_entity.description,
            context=domain_entity.context,
            layer=domain_entity.layer.value,
            bases=[t.model_dump(mode="json") for t in domain_entity.bases],
            # 级联映射子实体，需要注入外键 component_id
            attributes=[
                cls._attr_to_orm(attr, component_id=component_id_val)
                for attr in domain_entity.attributes
            ],
            behaviors=[
                cls._behavior_to_orm(beh, component_id=component_id_val)
                for beh in domain_entity.behaviors
            ],
        )

    @classmethod
    def _behavior_to_orm(
        cls, domain_entity: Behavior, component_id: ComponentId
    ) -> BehaviorModel:
        behavior_id_val = domain_entity.id.value

        return BehaviorModel(
            id=behavior_id_val,
            component_id=component_id.value,
            name=domain_entity.name,
            description=domain_entity.description,
            # Pydantic V2: model_dump(mode='json') 会自动将里面的所有类型(包括UUID, 枚举等)转为JSON兼容的基本类型
            scenarios=[s.model_dump(mode="json") for s in domain_entity.scenarios],
            output=domain_entity.output.model_dump(mode="json"),
            body=[s.model_dump(mode="json") for s in domain_entity.body],
            # Behavior 拥有的 inputs，注入外键 behavior_id
            inputs=[
                cls._attr_to_orm(attr, behavior_id=domain_entity.id)
                for attr in domain_entity.inputs
            ],
        )

    @classmethod
    def _attr_to_orm(
        cls,
        domain_entity: Attribute,
        component_id: ComponentId | None = None,
        behavior_id: BehaviorId | None = None,
    ) -> AttributeModel:
        """
        动态处理双重归属权：
        如果作为 Component 的属性，component_id 有值；
        如果作为 Behavior 的输入参数，behavior_id 有值。
        """
        value_dict = (
            expr_def_adapter.dump_python(domain_entity.value, mode="json")
            if domain_entity.value
            else None
        )
        type_def = (
            domain_entity.type.model_dump(mode="json")
            if domain_entity.type
            else None
        )
        return AttributeModel(
            id=domain_entity.id.value,
            component_id=component_id.value if component_id else None,
            behavior_id=behavior_id.value if behavior_id else None,
            name=domain_entity.name,
            description=domain_entity.description,
            # 递归值对象转为 JSON dict
            type_def=type_def,
            value=value_dict,
        )
