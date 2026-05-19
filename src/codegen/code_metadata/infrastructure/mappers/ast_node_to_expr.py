import ast

from codegen.code_metadata.application.dtos.call_expr_dto import CallExprDto
from codegen.code_metadata.application.dtos.dict_expr_dto import DictExprDto
from codegen.code_metadata.application.dtos.dict_item_dto import DictItemDto
from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr
from codegen.code_metadata.application.dtos.reference_expr_dto import ReferenceExprDto
from codegen.code_metadata.application.dtos.sequence_expr_dto import SequenceExprDto
from codegen.code_metadata.domain.value_objects.constant_expr import ConstantExpr


class AstNodeToExpr:
    
    def map(self, node: ast.expr | None) -> ParsedExpr | None:
        if node is None:
            return None
        return self.parse_ast_node(node)

    def parse_ast_node(self, node: ast.expr) -> ParsedExpr:
        match node:
            case ast.Constant(value=value):
                return ConstantExpr(value=value)
            case ast.Name():
                return self.parse_ast_name(node)
            case ast.Attribute():
                return self.parse_ast_attribute(node)
            case ast.Call():
                return self.parse_ast_call(node)
            case ast.List():
                return self.parse_ast_list(node)
            case ast.Tuple():
                return self.parse_ast_tuple(node)
            case ast.Set():
                return self.parse_ast_set(node)
            case ast.Dict():
                return self.parse_ast_dict(node)
            case _:
                raise ValueError(f"Unsupported AST node: {node}")

    def parse_ast_name(self, node: ast.Name) -> ReferenceExprDto:
        target = node.id
        source = None
        return ReferenceExprDto(
            target=target,
            source=source,
        )

    def parse_ast_attribute(self, node: ast.Attribute) -> ReferenceExprDto:
        target = node.attr
        source = self.parse_ast_node(node.value)
        return ReferenceExprDto(
            target=target,
            source=source,
        )

    def parse_ast_call(self, node: ast.Call) -> CallExprDto:
        callee = self.parse_ast_node(node.func)
        args = [self.parse_ast_node(arg) for arg in node.args]
        parsed_kwargs: dict[str, ParsedExpr] = {}
        for kw in node.keywords:
            if kw.arg is not None:
                parsed_kwargs[kw.arg] = self.parse_ast_node(kw.value)
            else:
                parsed_kwargs["**"] = self.parse_ast_node(kw.value)
        return CallExprDto(
            callee=callee,
            args=args,
            kwargs=parsed_kwargs,
        )

    def parse_ast_list(self, node: ast.List) -> SequenceExprDto:
        elements = [self.parse_ast_node(elt) for elt in node.elts]
        return SequenceExprDto(
            container_type="list",
            elements=elements,
        )

    def parse_ast_tuple(self, node: ast.Tuple) -> SequenceExprDto:
        elements = [self.parse_ast_node(elt) for elt in node.elts]
        return SequenceExprDto(
            container_type="tuple",
            elements=elements,
        )

    def parse_ast_set(self, node: ast.Set) -> SequenceExprDto:
        elements = [self.parse_ast_node(elt) for elt in node.elts]
        return SequenceExprDto(
            container_type="set",
            elements=elements,
        )

    def parse_ast_dict(self, node: ast.Dict) -> DictExprDto:
        items: list[DictItemDto] = []
        for k, v in zip(node.keys, node.values):
            parsed_key = self.parse_ast_node(k) if k is not None else None
            parsed_value = self.parse_ast_node(v)
            items.append(DictItemDto(key=parsed_key, value=parsed_value))
        return DictExprDto(items=items)
