import ast
from codegen.code_metadata.domain.aggregates.component import Component


class ComponentToAstClass:

    @staticmethod
    def map(component: Component) -> ast.ClassDef:
        body: list[ast.stmt] = []
        class_def = ast.ClassDef(
            name=component.name,
            bases=[],
            keywords=[],
            body=body,
        )
        return class_def