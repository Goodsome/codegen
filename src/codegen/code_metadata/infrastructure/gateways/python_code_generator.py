from dataclasses import dataclass
from typing import override

import ast

from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.infrastructure.mappers.component_to_ast_module import ComponentToAstModule
    

@dataclass
class PythonCodeGenerator(CodeGenerator):

    component_to_ast_module: ComponentToAstModule
    
    @override
    def generate(self, component: Component) -> str:
        module = self.component_to_ast_module.map(component)
        return ast.unparse(module)