
import ast
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.infrastructure.adapters.ast_builders import (
    import_builder,
    enum_builder,
    class_builder,
    function_builder
)

def build_module(module_spec: ModuleSpec, imports: list[ImportFromSpec]) -> ast.Module:
    """Builds an AST Module from a ModuleSpec and imports."""
    
    body: list[ast.stmt] = []
    
    # 1. Imports
    for imp in imports:
        body.append(import_builder.build_import(imp))
        
    # 2. Enums
    for enum_spec in module_spec.enums:
        body.append(enum_builder.build_enum(enum_spec))
        
    # 3. Classes
    for class_spec in module_spec.classes:
        body.append(class_builder.build_class(class_spec))
        
    # 4. Functions
    for func_spec in module_spec.functions:
        body.append(function_builder.build_function(func_spec))
        
    # Edge case: Empty body
    # ast.Module requires a body list, but empty is valid in Python (empty file).
    # However, if we want to be explicit, unparsing empty body creates empty file.
    
    return ast.Module(body=body, type_ignores=[])
