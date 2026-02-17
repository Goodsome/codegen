
import ast
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.imported_name import ImportedName

def parse_import(node: ast.Import | ast.ImportFrom) -> ImportFromSpec:
    """Parses an AST import node into an ImportFromSpec."""
    
    # Extract names from ast.alias objects
    imported_names: list[ImportedName] = []
    for alias in node.names:
        # ast.alias has 'name' and 'asname' (optional)
        imported_names.append(
            ImportedName(name=alias.name, alias=alias.asname)
        )
    
    if isinstance(node, ast.ImportFrom) and node.module:
        module = node.module
    else:
        module = "__root__"
        
    return ImportFromSpec(module=module, names=imported_names)
