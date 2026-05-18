import ast
from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.entities.attribute import Attribute
from codegen.code_metadata.domain.identifiers.component_id import ComponentId


class AttributeToAstAssign:
    
    def map(self, attribute: Attribute, dependencies: dict[ComponentId, ComponentDTO]) -> ast.AnnAssign:
        target = ast.Name(id=attribute.name, ctx=ast.Store())
        annotation = attribute.type.to_ast_node(components=dependencies)

        return ast.AnnAssign(
            target=target,
            annotation=annotation,
            simple=1,
        )