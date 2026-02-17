
import ast
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers import function_parser

def parse_class(node: ast.ClassDef) -> ClassSpec:
    """Parses an AST ClassDef into a ClassSpec."""
    
    name = node.name
    description = ast.get_docstring(node) or ""
    
    decorators = [ast.unparse(d) for d in node.decorator_list]
    inheritance = [ast.unparse(b) for b in node.bases]
    
    methods = []
    attributes = []
    
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(function_parser.parse_function(item))
        elif isinstance(item, (ast.AnnAssign, ast.Assign)):
            # parse_parameter_from_assign returns a list of ParameterSpec
            attrs = function_parser.parse_parameter_from_assign(item)
            attributes.extend(attrs)
            
    return ClassSpec.create(
        name=name,
        description=description,
        decorators=decorators,
        inheritance=inheritance,
        attributes=attributes,
        methods=methods,
    )
