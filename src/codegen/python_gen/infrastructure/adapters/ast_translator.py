
import ast
from dataclasses import dataclass
from codegen.python_gen.domain.ports.source_code_port import SourceCodePort
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.infrastructure.adapters.ast_builders import module_builder
from codegen.python_gen.infrastructure.adapters.ast_parsers import module_parser


@dataclass
class AstTranslator(SourceCodePort):
    """AST-based implementation of SourceCodePort."""

    def render_module(
        self, module_spec: ModuleSpec, imports: list[ImportFromSpec]
    ) -> str:
        """
        Renders a ModuleSpec into Python source code string.
        """
        # Build AST
        module_node = module_builder.build_module(module_spec, imports)
        
        # Fix locations
        ast.fix_missing_locations(module_node)
        
        # Unparse to string
        return ast.unparse(module_node)

    def parse_module(self, source_code: str, module_name: str) -> ModuleSpec:
        """
        Parses Python source code string into a ModuleSpec.
        """
        return module_parser.parse_module(source_code, module_name)
