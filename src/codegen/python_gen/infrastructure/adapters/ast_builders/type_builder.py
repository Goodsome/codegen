
import ast
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec

def build_type_annotation(type_spec: TypeAnnotationSpec) -> ast.expr:
    """Builds an AST type annotation from a specification."""
    
    # 1. Handle Union (A | B | C)
    if type_spec.name == "Union" and type_spec.args:
        if len(type_spec.args) == 1:
            return build_type_annotation(type_spec.args[0])
            
        current = build_type_annotation(type_spec.args[0])
        for arg in type_spec.args[1:]:
            right = build_type_annotation(arg)
            current = ast.BinOp(left=current, op=ast.BitOr(), right=right)
        return current

    # 2. Handle Container/Base Name
    container_node = _build_name_node(type_spec.name)

    # 3. Handle Generics (List[int], Dict[str, Any])
    if type_spec.args:
        args_nodes = [build_type_annotation(arg) for arg in type_spec.args]
        
        if len(args_nodes) == 1:
            slice_node = args_nodes[0]
        else:
            slice_node = ast.Tuple(elts=args_nodes, ctx=ast.Load())
            
        return ast.Subscript(
            value=container_node,
            slice=slice_node,
            ctx=ast.Load()
        )
        
    return container_node

def _build_name_node(name: str) -> ast.expr:
    """Helper to build Name or Attribute node (e.g. 'str' or 'typing.List')."""
    if name == "None":
        return ast.Constant(value=None)
        
    if "." in name:
        parts = name.split(".")
        value = ast.Name(id=parts[0], ctx=ast.Load())
        for part in parts[1:]:
            value = ast.Attribute(value=value, attr=part, ctx=ast.Load())
        return value
        
    return ast.Name(id=name, ctx=ast.Load())
