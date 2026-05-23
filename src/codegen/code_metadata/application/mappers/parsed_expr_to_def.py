from typing import Self
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.call_expr_dto import CallExprDto
from codegen.code_metadata.application.dtos.dict_expr_dto import DictExprDto
from codegen.code_metadata.application.dtos.dict_item_dto import DictItemDto
from codegen.code_metadata.application.dtos.lambda_expr_dto import LambdaExprDto
from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.reference_expr_dto import ReferenceExprDto
from codegen.code_metadata.application.dtos.sequence_expr_dto import SequenceExprDto
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.domain.value_objects.call_expr import CallExpr
from codegen.code_metadata.domain.value_objects.dict_expr import DictExpr
from codegen.code_metadata.domain.value_objects.dict_item import DictItem
from codegen.code_metadata.domain.value_objects.expr_def import ExprDef
from codegen.code_metadata.domain.value_objects.lambda_expr import LambdaExpr
from codegen.code_metadata.domain.value_objects.reference_expr import ReferenceExpr
from codegen.code_metadata.domain.value_objects.sequence_expr import SequenceExpr


@dataclass
class ParsedExprToDef:

    reference_resolver: ReferenceResolver

    @classmethod
    def create(
        cls,
        resolver: ReferenceResolver,
    ) -> Self:
        return cls(
            reference_resolver=resolver,
        )

    def map(self, expr: ParsedExpr | None) -> ExprDef | None:
        if expr is None:
            return None
        return self._map_expr(expr)

    def _map_expr(self, expr: ParsedExpr) -> ExprDef:
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
                raise ValueError(f"Unsupported expr kind: {expr.kind}")

    def _map_reference(
        self, expr: ReferenceExprDto,
    ) -> ReferenceExpr:
        
        source = self.map(expr.source)
        source_target = None
        if source and source.kind == ExprKind.REFERENCE:
            source_target = source.target

        target = self.reference_resolver.resolve_target(expr.target, source_target)
        
        return ReferenceExpr(
            target=target,
            source=source,
        )

    def _map_call(
        self, expr: CallExprDto,
    ) -> CallExpr:
        callee = self._map_expr(expr.callee)
        args = [self._map_expr(arg) for arg in expr.args]
        kwargs = {k: self._map_expr(v) for k, v in expr.kwargs.items()}
        return CallExpr(
            callee=callee,
            args=args,
            kwargs=kwargs,
        )

    def _map_sequence(
        self, expr: SequenceExprDto,
    ) -> SequenceExpr:
        
        container_type = expr.container_type
        elements = [self._map_expr(elem) for elem in expr.elements]
        return SequenceExpr(
            container_type=container_type,
            elements=elements,
        )

    def _map_dict(
        self, expr: DictExprDto,
    ) -> DictExpr:
        items = [self._map_dict_item(item) for item in expr.items]
        return DictExpr(items=items)

    def _map_dict_item(
        self, item: DictItemDto,
    ) -> DictItem:
        key = self._map_expr(item.key) if item.key else None
        value = self._map_expr(item.value)
        return DictItem(key=key, value=value)

    def _map_lambda(
        self, expr: LambdaExprDto,
    ) -> LambdaExpr:
        body = self._map_expr(expr.body)
        return LambdaExpr(
            params=expr.params,
            body=body,
        )