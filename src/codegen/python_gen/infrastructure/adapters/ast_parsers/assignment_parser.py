import ast
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.enums import AssignmentFlavor
from codegen.python_gen.domain.value_objects.call_spec import CallSpec
from codegen.python_gen.domain.value_objects.reference_spec import ReferenceSpec
from codegen.python_gen.domain.value_objects.literal_spec import LiteralSpec

def parse_assignment_value(node: ast.AST) -> AssignmentSpec:
    """Parses an AST expression into an AssignmentSpec."""
    
    if node is None:
        return None

    code_str = ""
    try:
        code_str = ast.unparse(node)
    except Exception:
        pass

    if isinstance(node, ast.Call):
        kwargs = {}
        for keyword in node.keywords:
            if keyword.arg:
               kwargs[keyword.arg] = parse_assignment_value(keyword.value)
        
        args = [parse_assignment_value(arg) for arg in node.args]
        
        func_name = ast.unparse(node.func)
        
        return AssignmentSpec(
            flavor=AssignmentFlavor.CALL,
            call=CallSpec(callee=func_name, args=args, kwargs=kwargs),
            code=code_str
        )

    elif isinstance(node, ast.Constant):
        return AssignmentSpec(
            flavor=AssignmentFlavor.LITERAL,
            literal=LiteralSpec(value=node.value),
            code=code_str
        )

    elif isinstance(node, ast.Name):
        return AssignmentSpec(
            flavor=AssignmentFlavor.SYMBOL,
            reference=ReferenceSpec(name=node.id),
            code=code_str
        )
    
    elif isinstance(node, ast.List):
        items = [parse_assignment_value(elt) for elt in node.elts]
        return AssignmentSpec(
            flavor=AssignmentFlavor.LIST,
            list_items=items,
            code=code_str
        )
        
    elif isinstance(node, ast.Dict):
        # Only support string keys for simple dicts mapping to DictSpec
        # Actually AssignmentSpec has dict_items: dict[str, AssignmentSpec]
        # This implies keys MUST be strings.
        is_simple_dict = True
        items = {}
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                items[k.value] = parse_assignment_value(v)
            else:
                is_simple_dict = False
                break

        if is_simple_dict:
             return AssignmentSpec(
                flavor=AssignmentFlavor.DICT,
                dict_items=items,
                code=code_str
            )

    elif isinstance(node, ast.Subscript):
        value_spec = parse_assignment_value(node.value)
        slice_spec = parse_assignment_value(node.slice)
        return AssignmentSpec.from_subscript(value_spec, slice_spec)
    
    # Fallback to CODE
    return AssignmentSpec(
        flavor=AssignmentFlavor.CODE,
        code=code_str
    )
