import ast
from dataclasses import dataclass
from codegen.code_metadata.application.dtos.parsed_type import ParsedType
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class AstNodeToParsedType:
    
    def parse_ast_node(self, node: ast.AST) -> ParsedType:
        if isinstance(node, ast.Expr):
            return self.parse_ast_expr(node)
        elif isinstance(node, ast.Name):
            return self.parse_ast_name(node)
        elif isinstance(node, ast.Subscript):
            return self.parse_ast_subscript(node)
        elif isinstance(node, ast.BinOp):
            return self.parse_ast_binop(node)
        elif isinstance(node, ast.Constant):
            return self.parse_ast_constant(node)
        elif isinstance(node, ast.Attribute):
            return self.parse_ast_attribute(node)
        raise NotImplementedError(f"Unsupported AST node: {node}, {ast.dump(node)}, {ast.unparse(node)}")

    def parse_ast_expr(self, expr: ast.Expr) -> ParsedType:
        return self.parse_ast_node(expr.value)

    def parse_ast_subscript(self, expr: ast.Subscript) -> ParsedType:
        container = self.parse_ast_node(expr.value)
        args: tuple[ParsedType, ...]
        if isinstance(expr.slice, ast.Tuple):
            args = tuple(self.parse_ast_node(slice) for slice in expr.slice.elts)
        else:
            args = (self.parse_ast_node(expr.slice),)

        container.args = args
        return container

    def parse_ast_name(self, expr: ast.Name) -> ParsedType:
        name = expr.id
        return ParsedType(origin=name)

    def parse_ast_binop(self, expr: ast.BinOp) -> ParsedType:
        match expr.op:
            case ast.BitOr():
                left_type = self.parse_ast_node(expr.left)
                right_type = self.parse_ast_node(expr.right)

                return ParsedType(
                    origin=PythonBuiltinType.UNION, args=(left_type, right_type)
                )
            case _:
                raise NotImplementedError(
                    f"不支持的类型注解二元操作符: {type(expr.op).__name__} (节点: {ast.dump(expr)})"
                )

    def parse_ast_constant(self, expr: ast.Constant) -> ParsedType:
        """
        处理常量节点。在类型注解中，主要用于处理省略号 (...) 和 前向引用 (字符串)。
        """
        match expr.value:
            case val if val is ...:
                return ParsedType(
                    origin=PythonBuiltinType.ELLIPSIS
                )
                
            case str(forward_ref_name):
                return ParsedType(
                    origin=forward_ref_name
                )
                
            case None:
                return ParsedType(origin=PythonBuiltinType.NONE)
                
            case _:
                raise NotImplementedError(
                    f"不支持的类型注解常量值: {expr.value} (节点: {ast.dump(expr)})"
                )

    def parse_ast_attribute(self, expr: ast.Attribute) -> ParsedType:
        origin = ast.unparse(expr)
        return ParsedType(
            origin=origin,
        )
        