from dataclasses import dataclass
from typing import override

import ast

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.infrastructure.mappers.component_to_ast_module import ComponentToAstModule
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
    

@dataclass
class PythonCodeGenerator(CodeGenerator):

    component_to_ast_module: ComponentToAstModule
    
    @override
    def generate(self, component: Component, dep_components: dict[ComponentId, ComponentDTO]) -> str:
        module = self.component_to_ast_module.map(component, dep_components=dep_components)
        return ast.unparse(module)