import ast

from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent


class AstClassToComponent:
    @staticmethod
    def map(node: ast.ClassDef) -> ParsedComponent:
        
        bases = [ast.unparse(b) for b in node.bases]
        
        return ParsedComponent(
            name=node.name,
            description=ast.get_docstring(node) or "",
            bases=bases
        )
