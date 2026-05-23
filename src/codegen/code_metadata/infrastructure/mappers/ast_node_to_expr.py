import ast

from codegen.code_metadata.application.dtos.call_expr_dto import CallExprDto
from codegen.code_metadata.application.dtos.dict_expr_dto import DictExprDto
from codegen.code_metadata.application.dtos.dict_item_dto import DictItemDto
from codegen.code_metadata.application.dtos.lambda_expr_dto import LambdaExprDto
from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.reference_expr_dto import ReferenceExprDto
from codegen.code_metadata.application.dtos.sequence_expr_dto import SequenceExprDto
from codegen.code_metadata.domain.value_objects.constant_expr import ConstantExpr


class AstNodeToExpr:
    
    def _node_to_expr(self, node: ast.expr) -> ParsedExpr:
        match node:
            case ast.Constant(value=value):
                return ConstantExpr(value=value)
            case ast.Name():
                return self.name_to_expr(node)
            case ast.Attribute():
                return self.attribute_to_expr(node)
            case ast.Call():
                return self.call_to_expr(node)
            case ast.List():
                return self.list_to_expr(node)
            case ast.Tuple():
                return self.tuple_to_expr(node)
            case ast.Set():
                return self.set_to_expr(node)
            case ast.Dict():
                return self.dict_to_expr(node)
            case ast.Lambda():
                return self.lambda_to_expr(node)
            case _:
                raise ValueError(f"Unsupported AST node: {node}")

    def name_to_expr(self, node: ast.Name) -> ReferenceExprDto:
        target = node.id
        source = None
        return ReferenceExprDto(
            target=target,
            source=source,
        )

    def attribute_to_expr(self, node: ast.Attribute) -> ReferenceExprDto:
        target = node.attr
        source = self._node_to_expr(node.value)
        return ReferenceExprDto(
            target=target,
            source=source,
        )

    def call_to_expr(self, node: ast.Call) -> CallExprDto:
        callee = self._node_to_expr(node.func)
        args = [self._node_to_expr(arg) for arg in node.args]
        parsed_kwargs: dict[str, ParsedExpr] = {}
        for kw in node.keywords:
            if kw.arg is not None:
                parsed_kwargs[kw.arg] = self._node_to_expr(kw.value)
            else:
                parsed_kwargs["**"] = self._node_to_expr(kw.value)
        return CallExprDto(
            callee=callee,
            args=args,
            kwargs=parsed_kwargs,
        )

    def list_to_expr(self, node: ast.List) -> SequenceExprDto:
        elements = [self._node_to_expr(elt) for elt in node.elts]
        return SequenceExprDto(
            container_type="list",
            elements=elements,
        )

    def tuple_to_expr(self, node: ast.Tuple) -> SequenceExprDto:
        elements = [self._node_to_expr(elt) for elt in node.elts]
        return SequenceExprDto(
            container_type="tuple",
            elements=elements,
        )

    def set_to_expr(self, node: ast.Set) -> SequenceExprDto:
        elements = [self._node_to_expr(elt) for elt in node.elts]
        return SequenceExprDto(
            container_type="set",
            elements=elements,
        )

    def dict_to_expr(self, node: ast.Dict) -> DictExprDto:
        items: list[DictItemDto] = []
        for k, v in zip(node.keys, node.values):
            parsed_key = self._node_to_expr(k) if k is not None else None
            parsed_value = self._node_to_expr(v)
            items.append(DictItemDto(key=parsed_key, value=parsed_value))
        return DictExprDto(items=items)

    def lambda_to_expr(self, node: ast.Lambda) -> LambdaExprDto:
        params = [arg.arg for arg in node.args.args]
        if node.args.vararg:
            params.append(f"*{node.args.vararg.arg}")
        params += [arg.arg for arg in node.args.kwonlyargs]
        if node.args.kwarg:
            params.append(f"**{node.args.kwarg.arg}")
        body = self._node_to_expr(node.body)
        return LambdaExprDto(params=params, body=body)
