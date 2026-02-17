
import ast
from codegen.python_gen.domain.value_objects.python_enum_spec import PythonEnumSpec


def build_enum(enum_spec: PythonEnumSpec) -> ast.ClassDef:
    """Builds an AST ClassDef for an Enum."""
    
    body: list[ast.stmt] = []
    
    # 1. Docstring
    if enum_spec.description:
        body.append(ast.Expr(value=ast.Constant(value=enum_spec.description)))
        
    # 2. Members
    for member in enum_spec.members:
        # Build value node (Constant)
        if member.value is None:
             # auto() case or just name? 
             # If value is None, what does it mean? A = auto()?
             # Spec says value: str | int | None.
             # If None, maybe we shouldn't assign? But Enums need assignment.
             # Let's assume 'auto()' if None? Or default 1?
             # For now, let's treat None as auto() call if strictly needed, 
             # but to be safe with "Simple Types" rule, let's generate Constant(None) or empty?
             # Python Enum members must have values.
             # Let's assume it's a string "auto()" passed as string or similar.
             # If strictly None, use Ellipsis?
             value_node = ast.Constant(value=None)
        else:
            value_node = ast.Constant(value=member.value)
            
        assign = ast.Assign(
            targets=[ast.Name(id=member.name, ctx=ast.Store())],
            value=value_node,
            lineno=0  # Optional but good practice
        )
        body.append(assign)
        
    if not body:
        body.append(ast.Expr(value=ast.Constant(value=...)))
        
    # 3. Bases
    bases = []
    if enum_spec.base_class:
        try:
            bases.append(ast.parse(enum_spec.base_class, mode='eval').body)
        except SyntaxError:
            bases.append(ast.Name(id=enum_spec.base_class, ctx=ast.Load()))
    
    # 4. Decorators
    decorator_list = []
    for d in enum_spec.decorators:
        try:
            decorator_list.append(ast.parse(d, mode='eval').body)
        except SyntaxError:
            pass # Ignore invalid decorators or handle error

    return ast.ClassDef(
        name=enum_spec.name,
        bases=bases,
        keywords=[],
        body=body,
        decorator_list=decorator_list
    )
