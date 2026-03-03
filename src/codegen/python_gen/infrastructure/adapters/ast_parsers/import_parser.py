
import ast
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.imported_name import ImportedName

def parse_import(node: ast.Import | ast.ImportFrom) -> ImportFromSpec:
    """Parses an AST import node into an ImportFromSpec."""
    
    # Extract names from ast.alias objects
    imported_names = frozenset(
        ImportedName(name=alias.name, alias=alias.asname)
        for alias in node.names
    )
    
    if isinstance(node, ast.ImportFrom) and node.module:
        module = node.module
    else:
        module = "__root__"
        
    return ImportFromSpec(module=module, names=imported_names)
