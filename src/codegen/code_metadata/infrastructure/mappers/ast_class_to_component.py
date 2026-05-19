import ast
from dataclasses import dataclass

from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.infrastructure.mappers.ast_node_to_attribute import (
    AstNodeToParsedAttribute,
)
from codegen.code_metadata.infrastructure.mappers.ast_node_to_parsed_type import (
    AstNodeToParsedType,
)


@dataclass
class AstClassToComponent:
    ast_node_to_parsed_type: AstNodeToParsedType
    ast_node_to_attribute: AstNodeToParsedAttribute

    def map(self, node: ast.ClassDef) -> ParsedComponent:
        bases = [self.ast_node_to_parsed_type.parse_ast_node(b) for b in node.bases]

        attributes: list[ParsedAttribute] = []
        for item in node.body:
            pa = self.ast_node_to_attribute.map(item)
            if pa is None:
                continue
            attributes.append(pa)

        return ParsedComponent(
            name=node.name,
            description=ast.get_docstring(node) or "",
            bases=bases,
            attributes=attributes,
        )
