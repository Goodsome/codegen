import ast
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.infrastructure.mappers.ast_node_to_expr import AstNodeToExpr
from codegen.code_metadata.infrastructure.mappers.ast_node_to_parsed_type import AstNodeToParsedType


@dataclass
class AstNodeToParsedAttribute:

    ast_node_to_parsed_type: AstNodeToParsedType
    ast_node_to_expr: AstNodeToExpr

    def map(self, node: ast.AST | None) -> ParsedAttribute | None:
        if node is None:
            return None
        return self.map_ast(node)

    def map_ast(self, node: ast.AST) -> ParsedAttribute | None:
        match node:
            case ast.AnnAssign():
                return self.map_ann_assign(node)
            case ast.Assign():
                return self.map_assign(node)
            case _:
                return None
    
    def map_ann_assign(self, node: ast.AnnAssign) -> ParsedAttribute:
        if isinstance(node.target, ast.Name):
            name = node.target.id
        else:
            raise ValueError(f"Unsupported AST node: {node}")
            
        _type = self.ast_node_to_parsed_type.parse_ast_node(node.annotation)
        value = self.ast_node_to_expr.map(node.value)
        
        return ParsedAttribute(
            name=name,
            description="",
            type=_type,
            value=value,
        )

    def map_assign(self, node: ast.Assign) -> ParsedAttribute:
        if len(node.targets) != 1:
            raise ValueError(f"Unsupported AST node: {node}")
        target = node.targets[0]
        if isinstance(target, ast.Name):
            name = target.id
        else:
            raise ValueError(f"Unsupported AST node: {node}")
        
        value = self.ast_node_to_expr.map(node.value)
        return ParsedAttribute(
            name=name,
            description="",
            type=None,
            value=value,
        )