
import ast
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec

_TYPE_NAME_MAPPING: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "String": "str",
    "List": "list",
    "Dict": "dict",
    "Set": "set",
    "Tuple": "tuple",
    "void": "None",
    "boolean": "bool",
}

def parse_type(node: ast.AST | None) -> TypeAnnotationSpec:
    """Parses an AST type annotation into a TypeAnnotationSpec."""
    if node is None:
        return TypeAnnotationSpec(name="Any")

    # 1. Handle Names (int, str, List)
    if isinstance(node, ast.Name):
        type_name = node.id
        mapped_name = _TYPE_NAME_MAPPING.get(type_name, type_name)
        return TypeAnnotationSpec(name=mapped_name)

    # 2. Handle Constants (None)
    if isinstance(node, ast.Constant):
        if node.value is None:
            return TypeAnnotationSpec(name="None")
        return TypeAnnotationSpec(name=str(node.value))

    # 3. Handle Subscripts (List[int])
    if isinstance(node, ast.Subscript):
        # Recursively parse the container (e.g., List)
        # Note: node.value could be Name or Attribute
        container_spec = parse_type(node.value)
        
        args_specs = []
        slice_node = node.slice
        
        if isinstance(slice_node, ast.Tuple):
            args_specs = [parse_type(elt) for elt in slice_node.elts]
        else:
            args_specs = [parse_type(slice_node)]
            
        return TypeAnnotationSpec(name=container_spec.name, args=args_specs)

    # 4. Handle Union (A | B)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left = parse_type(node.left)
        right = parse_type(node.right)
        
        merged_args = []
        
        if left.name == "Union":
            merged_args.extend(left.args)
        else:
            merged_args.append(left)
            
        if right.name == "Union":
            merged_args.extend(right.args)
        else:
            merged_args.append(right)
            
        return TypeAnnotationSpec(name="Union", args=merged_args)

    # 5. Handle Attributes (typing.List)
    if isinstance(node, ast.Attribute):
        value_spec = parse_type(node.value)
        return TypeAnnotationSpec(name=f"{value_spec.name}.{node.attr}")

    # Fallback
    try:
        return TypeAnnotationSpec(name=ast.unparse(node))
    except Exception:
        return TypeAnnotationSpec(name="Any")

def parse_type_str(annotation: str) -> TypeAnnotationSpec:
    """Parses a type annotation string into a TypeAnnotationSpec."""
    if not annotation:
        raise ValueError("Annotation string cannot be empty")
        
    try:
        tree = ast.parse(annotation, mode="eval")
        return parse_type(tree.body)
    except SyntaxError as e:
        raise ValueError(f"Invalid type annotation syntax: {annotation}") from e
