import ast
from dataclasses import dataclass
from typing import override

from codegen.code_metadata.domain.aggregates import FileModule
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.factories.component_policy_factory import (
    ComponentPolicyFactory,
)
from codegen.code_metadata.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.domain.services.translate_reference import TranslateReference
from codegen.code_metadata.infrastructure.mappers.component_to_ast_module import (
    ComponentToAstModule,
)


@dataclass
class PythonCodeGenerator(CodeGenerator):
    component_policy_factory: ComponentPolicyFactory

    @override
    def generate(
        self,
        component: Component,
        resolver: TranslateReference,
    ) -> str:
        mapper = ComponentToAstModule(
            resolver=resolver,
            component_policy_factory=self.component_policy_factory,
        )
        module = mapper.to_ast_module(component)
        ast.fix_missing_locations(module)
        return ast.unparse(module)

    @override
    def generate_module_code(
        self,
        module: FileModule,
        resolver: TranslateReference
    ) -> str:
        mapper = ComponentToAstModule(
            resolver=resolver,
            component_policy_factory=self.component_policy_factory,
        )
        ast_module = mapper.module_to_ast(module)
        ast.fix_missing_locations(ast_module)
        return ast.unparse(ast_module)