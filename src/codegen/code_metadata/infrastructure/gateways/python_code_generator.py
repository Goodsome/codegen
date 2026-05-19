from dataclasses import dataclass
from typing import override

import ast

from codegen.code_metadata.application.dtos.component_dto import ComponentDTO
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.factories.component_policy_factory import ComponentPolicyFactory
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.domain.services.reference_resolver import ReferenceResolver
from codegen.code_metadata.infrastructure.mappers.component_to_ast_module import ComponentToAstModule
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
    

@dataclass
class PythonCodeGenerator(CodeGenerator):

    component_policy_factory: ComponentPolicyFactory
    
    @override
    def generate(
        self, component: Component, dep_components: dict[ComponentId, ComponentDTO],
        resolver: ReferenceResolver,
    ) -> str:
        mapper = ComponentToAstModule.create(
            self.component_policy_factory,
            resolver=resolver,
        )
        module = mapper.map(component, dep_components=dep_components)
        ast.fix_missing_locations(module)
        return ast.unparse(module)