from dataclasses import dataclass, field
from typing import assert_never, overload

from codegen.code_metadata.application.dtos.call_expr_dto import CallExprDto
from codegen.code_metadata.application.dtos.dict_expr_dto import DictExprDto
from codegen.code_metadata.application.dtos.dict_item_dto import DictItemDto
from codegen.code_metadata.application.dtos.lambda_expr_dto import LambdaExprDto
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_behavior import ParsedBehavior
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.code_metadata.application.dtos.reference_expr_dto import ReferenceExprDto
from codegen.code_metadata.application.dtos.sequence_expr_dto import SequenceExprDto
from codegen.code_metadata.domain.aggregates.component import ClassComponent, Component, UnionComponent
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.entities.behavior import Behavior
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.attribute_id import AttributeId
from codegen.code_metadata.domain.identifiers.behavior_id import BehaviorId
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.registries.component_registry import ComponentRegistry
from codegen.code_metadata.domain.services.path_parser import PathParser
from codegen.code_metadata.domain.value_objects.call_expr import CallExpr
from codegen.code_metadata.domain.value_objects.dict_expr import DictExpr
from codegen.code_metadata.domain.value_objects.dict_item import DictItem
from codegen.code_metadata.domain.value_objects.expr_def import ExprDef
from codegen.code_metadata.domain.value_objects.lambda_expr import LambdaExpr
from codegen.code_metadata.domain.value_objects.reference_expr import ReferenceExpr
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.code_metadata.domain.value_objects.sequence_expr import SequenceExpr
from codegen.code_metadata.domain.value_objects.type_def import TypeDef


@dataclass
class SyncModuleContext:
    
    module_id: ModuleId
    module: ParsedFileModule
    component_registry: ComponentRegistry
    path_parser: PathParser

    def parsed_component_to_component(self, parsed_component: ParsedComponent) -> Component:
        if parsed_component.is_union:
            component = self.parsed_component_to_union_component(parsed_component)
        else:
            component = self.parsed_component_to_class_component(parsed_component)
        self.component_registry.register(component)
        return component

    def parsed_component_to_class_component(self, parsed_component: ParsedComponent) -> ClassComponent:
        component = self.component_registry.find_by_name(parsed_component.name)
        if isinstance(component, UnionComponent):
            raise ValueError(f"not support {component=}")
        if component is None:
            component_id = ComponentId.create()
        else:
            component_id = component.id

        parsed_path = self.path_parser.parse_file_path(self.module.path)
        bases = [self.parsed_type_to_type_def(parsed_type) for parsed_type in parsed_component.bases]
        attributes = [self.parsed_attribute_to_attribute(a, component) for a in parsed_component.attributes]
        behaviors = [self.parsed_behavior_to_behavior(b, component) for b in parsed_component.behaviors]

        return ClassComponent(
            module_id=self.module_id,
            id=component_id,
            name=parsed_component.name,
            context=parsed_path.context,
            layer=parsed_path.layer,
            type=parsed_path.component_type,
            description=parsed_component.description,
            bases=bases,
            attributes=attributes,
            behaviors=behaviors,
        )

    def parsed_component_to_union_component(self, parsed_component: ParsedComponent) -> UnionComponent:
        component = self.component_registry.find_by_name(parsed_component.name)
        if component is None:
            component_id = ComponentId.create()
        else:
            component_id = component.id
            
        parsed_path = self.path_parser.parse_file_path(self.module.path)
        members = self.parsed_members_to_component_ids(parsed_component.members)
        members_v2 = [ReferenceTarget(raw=m) for m in parsed_component.members]

        return UnionComponent(
            id=component_id,
            module_id=self.module_id,
            name=parsed_component.name,
            context=parsed_path.context,
            layer=parsed_path.layer,
            type=parsed_path.component_type,
            description=parsed_component.description,
            members=members,
            discriminator=parsed_component.discriminator,
            members_v2=members_v2,
        )

    @overload
    def parsed_type_to_type_def(self, parsed_type: ParsedType) -> TypeDef:
        ...

    @overload
    def parsed_type_to_type_def(self, parsed_type: None) -> None:
        ...

    def parsed_type_to_type_def(self, parsed_type: ParsedType | None) -> TypeDef | None:
        if parsed_type is None:
            return None
        origin = self.resolve_target(parsed_type.origin)
        args = tuple(self.parsed_type_to_type_def(arg) for arg in parsed_type.args)
        return TypeDef(origin=origin, args=args)
    
    def resolve_target(
        self, target: str
    ) -> ReferenceTarget:
        
        return ReferenceTarget(raw=target)

    @overload
    def parsed_expr_to_expr_def(self, expr: None) -> None:
        ...

    @overload
    def parsed_expr_to_expr_def(self, expr: ParsedExpr) -> ExprDef:
        ...

    def parsed_expr_to_expr_def(self, expr: ParsedExpr | None) -> ExprDef | None:
        if expr is None:
            return None
        match expr.kind:
            case ExprKind.CONSTANT:
                return expr
            case ExprKind.REFERENCE:
                return self._map_reference(expr)
            case ExprKind.CALL:
                return self._map_call(expr)
            case ExprKind.SEQUENCE:
                return self._map_sequence(expr)
            case ExprKind.DICT:
                return self._map_dict(expr)
            case ExprKind.LAMBDA:
                return self._map_lambda(expr)
            case _:
                assert_never(expr.kind)

    def _map_reference(
        self,
        expr: ReferenceExprDto,
    ) -> ReferenceExpr:
        source = self.parsed_expr_to_expr_def(expr.source)
        target = self.resolve_target(expr.target)

        return ReferenceExpr(
            target=target,
            source=source,
        )

    def _map_call(
        self,
        expr: CallExprDto,
    ) -> CallExpr:
        callee = self.parsed_expr_to_expr_def(expr.callee)
        args = [self.parsed_expr_to_expr_def(arg) for arg in expr.args]
        kwargs = {k: self.parsed_expr_to_expr_def(v) for k, v in expr.kwargs.items()}
        return CallExpr(
            callee=callee,
            args=args,
            kwargs=kwargs,
        )

    def _map_sequence(
        self,
        expr: SequenceExprDto,
    ) -> SequenceExpr:
        container_type = expr.container_type
        elements = [self.parsed_expr_to_expr_def(elem) for elem in expr.elements]
        return SequenceExpr(
            container_type=container_type,
            elements=elements,
        )

    def _map_dict(
        self,
        expr: DictExprDto,
    ) -> DictExpr:
        items = [self._map_dict_item(item) for item in expr.items]
        return DictExpr(items=items)

    def _map_dict_item(
        self,
        item: DictItemDto,
    ) -> DictItem:
        key = self.parsed_expr_to_expr_def(item.key) if item.key else None
        value = self.parsed_expr_to_expr_def(item.value)
        return DictItem(key=key, value=value)

    def _map_lambda(
        self,
        expr: LambdaExprDto,
    ) -> LambdaExpr:
        body = self.parsed_expr_to_expr_def(expr.body)
        return LambdaExpr(
            params=expr.params,
            body=body,
        )

    def parsed_attribute_to_attribute(
        self,
        parsed_attribute: ParsedAttribute,
        component: ClassComponent | None,
    ) -> Attribute:
        if component is not None:
            attribute = component.find_attribute(parsed_attribute.name)
        else:
            attribute = None

        if attribute is None:
            attribute_id = AttributeId.create()
        else:
            attribute_id = attribute.id
        type_def = self.parsed_type_to_type_def(parsed_attribute.type)
        return Attribute(
            id=attribute_id,
            name=parsed_attribute.name,
            type=type_def,
            value_v2=parsed_attribute.value_v2,
        )

    def parsed_behavior_to_behavior(self, parsed_behavior: ParsedBehavior, component: ClassComponent | None) -> Behavior:
        if component is not None:
            behavior = component.find_behavior(parsed_behavior.name)
        else:
            behavior = None
        if behavior is None:
            behavior_id = BehaviorId.create()
        else:
            behavior_id = behavior.id
        inputs = [self.parsed_attribute_to_attribute(a, component) for a in parsed_behavior.inputs]
        output = self.parsed_type_to_type_def(parsed_behavior.output)
        return Behavior(
            id=behavior_id,
            name=parsed_behavior.name,
            description=parsed_behavior.description or "",
            scenarios=[],
            inputs=inputs,
            output=output,
            body=parsed_behavior.body,
        )

    def parsed_members_to_component_ids(
        self,
        parsed_members: list[str],
    ) -> list[ComponentId]:
        component_ids: list[ComponentId] = []
        for name in parsed_members:
            component = self.component_registry.find_by_name(name)
            if component is None:
                continue
            component_ids.append(component.id)

        return component_ids
