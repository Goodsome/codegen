
import ast
from codegen.python_gen.domain.value_objects.python_enum_spec import PythonEnumSpec
from codegen.python_gen.domain.value_objects.python_enum_member_spec import PythonEnumMemberSpec

def parse_enum(node: ast.ClassDef) -> PythonEnumSpec:
    """Parses an AST ClassDef into a PythonEnumSpec."""
    
    name = node.name
    description = ast.get_docstring(node) or ""
    
    decorators = []
    for d in node.decorator_list:
        decorators.append(ast.unparse(d))
        
    base_class = "Enum"
    if node.bases:
        base_class = ast.unparse(node.bases[0])
        
    members = []
    for item in node.body:
        # Check for Assignments (A = 1)
        if isinstance(item, ast.Assign):
            targets = item.targets
            # Filter out __doc__ or other dunder names if necessary?
            # Usually docstring is Expr, not Assign.
            
            for target in targets:
                if isinstance(target, ast.Name):
                     # Skip private/special names if needed
                    # if target.id.startswith("_") ...
                    
                    member_name = target.id
                    
                    # Parse Value
                    member_value = _parse_value(item.value)
                    
                    members.append(PythonEnumMemberSpec.create(
                        name=member_name,
                        value=member_value
                    ))
        
        # Also need to handle AnnAssign (A: int = 1) if supported?
        # Enums usually use Assign.
        
    return PythonEnumSpec.create(
        name=name,
        description=description,
        decorators=decorators,
        base_class=base_class,
        members=members
    )

def _parse_value(node: ast.AST) -> str | int | None:
    if isinstance(node, ast.Constant):
        return node.value
    # If it is not a constant (e.g. Call auto()), unparse it to string
    # This matches the behavior discussed: complex values become code strings.
    # Note: enum_builder currently only supports Constants. 
    # Round-trip for auto() will currently convert parsing -> "auto()" -> builder -> Constant("auto()") -> A = "auto()".
    # This is a known limitation for now.
    return ast.unparse(node)
