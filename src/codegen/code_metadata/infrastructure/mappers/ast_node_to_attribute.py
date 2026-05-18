import ast
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.infrastructure.mappers.ast_node_to_parsed_type import AstNodeToParsedType


@dataclass
class AstNodeToParsedAttribute:

    ast_node_to_parsed_type: AstNodeToParsedType
    
    def ann_assign_to_attribute(self, node: ast.AnnAssign) -> ParsedAttribute:
        if isinstance(node.target, ast.Name):
            name = node.target.id
        else:
            raise
        node.annotation
        
        _type = self.ast_node_to_parsed_type.parse_ast_node(node.annotation)
        return ParsedAttribute(
            name=name,
            description="",
            type=_type
        )