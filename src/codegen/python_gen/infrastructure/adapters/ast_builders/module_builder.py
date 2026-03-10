
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
    regular_imports = [i for i in imports if not i.type_checking]
    type_checking_imports = [i for i in imports if i.type_checking]

    for imp in regular_imports:
        body.append(import_builder.build_import(imp))
        
    if type_checking_imports:
        if_body = []
        for imp in type_checking_imports:
            if_body.append(import_builder.build_import(imp))
            
        type_checking_node = ast.If(
            test=ast.Name(id="TYPE_CHECKING", ctx=ast.Load()),
            body=if_body,
            orelse=[]
        )
        body.append(type_checking_node)

    # 1.5 Extra Code (type definitions, comments, etc.)
    for raw in module_spec.extra_code:
        try:
             # Parse raw code string back to AST nodes
             nodes = ast.parse(raw.code).body
             body.extend(nodes)
        except SyntaxError:
             # Should not happen if it came from valid source, but safety first.
             pass

    # 2. Assignments (must come after extra_code so type references are resolved)
    for assignment in module_spec.assignments:
        if assignment.type_annotation:
            # AnnAssign
            stmt = ast.AnnAssign(
                target=ast.Name(id=assignment.name, ctx=ast.Store()),
                annotation=ast.parse(assignment.type_annotation).body[0].value,
                value=ast.parse(assignment.value).body[0].value if assignment.value else None,
                simple=1
            )
        else:
            # Assign
            stmt = ast.Assign(
                targets=[ast.Name(id=assignment.name, ctx=ast.Store())],
                value=ast.parse(assignment.value).body[0].value
            )
        body.append(stmt)
        
    # 3. Enums
    for enum_spec in module_spec.enums:
        body.append(enum_builder.build_enum(enum_spec))
        
    # 4. Classes
    for class_spec in module_spec.classes:
        body.append(class_builder.build_class(class_spec))
        
    # 5. Functions
    for func_spec in module_spec.functions:
        body.append(function_builder.build_function(func_spec))
             
    # Edge case: Empty body
    # ast.Module requires a body list, but empty is valid in Python (empty file).
    # However, if we want to be explicit, unparsing empty body creates empty file.
    
    return ast.Module(body=body, type_ignores=[])
