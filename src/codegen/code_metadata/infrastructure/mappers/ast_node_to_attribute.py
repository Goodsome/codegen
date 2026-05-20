import ast
from codegen.code_metadata.application.dtos.parsed_attribute import ParsedAttribute
from codegen.code_metadata.infrastructure.mappers.ast_mapper_protocol import (
    AstMapperProtocol,
)


class AstNodeToAttribute:
    
    def ann_assign_to_attribute(
        self: AstMapperProtocol, node: ast.AnnAssign
    ) -> ParsedAttribute:
        if isinstance(node.target, ast.Name):
            name = node.target.id
        else:
            raise ValueError(f"Unsupported AST node: {node}")

        _type = self.parse_node_to_type(node.annotation)
        value = self.parse_node_to_expr(node.value) if node.value else None

        return ParsedAttribute(
            name=name,
            description="",
            type=_type,
            value=value,
        )

    def assign_to_attribute(
        self: AstMapperProtocol, node: ast.Assign
    ) -> ParsedAttribute:
        if len(node.targets) != 1:
            raise ValueError(f"Unsupported AST node: {node}")
        target = node.targets[0]
        if isinstance(target, ast.Name):
            name = target.id
        else:
            raise ValueError(f"Unsupported AST node: {node}")

        value = self.parse_node_to_expr(node.value)
        return ParsedAttribute(
            name=name,
            description="",
            type=None,
            value=value,
        )

    def arg_to_attribute(
        self: AstMapperProtocol, node: ast.arg
    ) -> ParsedAttribute:
        name = node.arg
        _type = self.parse_node_to_type(node.annotation) if node.annotation else None
        return ParsedAttribute(
            name=name,
            description="",
            type=_type,
            value=None
        )
        
    def _parse_node_to_attributes(self: AstMapperProtocol, node: ast.arguments) -> list[ParsedAttribute]:
        result: list[ParsedAttribute] = []

        # Positional-only + regular positional args share one defaults list,
        # which is right-aligned (i.e. the last N args get the N defaults).
        pos_args = node.posonlyargs + node.args
        offset = len(pos_args) - len(node.defaults)
        for i, arg in enumerate(pos_args):
            attr = self.parse_node_to_attribute(arg)
            default_idx = i - offset
            if default_idx >= 0:
                attr.value = self.parse_node_to_expr(node.defaults[default_idx])
            result.append(attr)

        if node.vararg:
            result.append(self.parse_node_to_attribute(node.vararg))

        for i, arg in enumerate(node.kwonlyargs):
            attr = self.parse_node_to_attribute(arg)
            kw_default = node.kw_defaults[i]
            if kw_default is not None:
                attr.value = self.parse_node_to_expr(kw_default)
            result.append(attr)

        if node.kwarg:
            result.append(self.parse_node_to_attribute(node.kwarg))

        return result