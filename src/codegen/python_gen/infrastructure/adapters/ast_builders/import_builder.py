
import ast
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec

def build_import(import_spec: ImportFromSpec) -> ast.Import | ast.ImportFrom:
    """Builds an AST import node from an ImportFromSpec."""
    
    names = [
        ast.alias(name=n.name, asname=n.alias if n.alias else None) 
        for n in import_spec.names
    ]
    
    if import_spec.module == "__root__":
        return ast.Import(names=names)
    
    return ast.ImportFrom(
        module=import_spec.module,
        names=names,
        level=import_spec.level
    )
