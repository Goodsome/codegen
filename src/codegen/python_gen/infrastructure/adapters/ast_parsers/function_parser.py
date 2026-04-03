
import ast
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers import type_parser, assignment_parser
# Need FieldSpec logic? Reusing parsers?
# ParameterSpec definition has logic for defaults?
# ParameterSpec logic is limited. 
# We need to parse AST back to Spec.

def parse_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionSpec:
    """Parses an AST FunctionDef into a FunctionSpec."""
    
    # 1. Parsing Parameters
    params = []
    # node.args.args
    # Skip 'self' or 'cls' based on detection?
    # FunctionSpec.parse_ast logic does this.
    # We should detect type first.
    
    decorators = [ast.unparse(d) for d in node.decorator_list]
    
    first_arg_name = None
    if node.args.args:
        first_arg_name = node.args.args[0].arg

    # Determine type
    # Logic copied/adapted from FunctionSpec.parse_ast
    # To avoid importing Domain Enum, we can perform checks.
    # But FunctionSpec expects FunctionType enum.
    # We should import it.
    
    # Wait, simple detection:
    is_class_method = any("classmethod" in d for d in decorators)
    is_static_method = any("staticmethod" in d for d in decorators)
    is_instance = not is_class_method and not is_static_method and first_arg_name == "self"
    
    for i, arg in enumerate(node.args.args):
        # Default value?
        # defaults list aligns with end of args.
        defaults_count = len(node.args.args) - len(node.args.defaults)
        
        assignment = None
        if i >= defaults_count:
            # This arg has a default
            default_index = i - defaults_count
            default_node = node.args.defaults[default_index]
            
            assignment = assignment_parser.parse_assignment_value(default_node)

        anno = type_parser.parse_type(arg.annotation)
        params.append(VariableSpec.create(name=arg.arg, type_spec=anno, assignment=assignment))

    # 2. Return Type
    return_annotation = type_parser.parse_type(node.returns)
    
    # 3. Suite (skip docstring since it's extracted to description separately)
    suite = ""
    if node.body:
        # Filter out docstring from body since it's stored separately in description
        body_without_doc = node.body
        if ast.get_docstring(node):
            body_without_doc = node.body[1:] if len(node.body) > 1 else []
        suite = "\n".join([ast.unparse(b) for b in body_without_doc])

    # 4. Create Spec
    # Need to map to FunctionType enum.
    from codegen.python_gen.domain.enums import FunctionType
    ft = FunctionType.FUNCTION
    if is_class_method:
        ft = FunctionType.CLASS_METHOD
    elif is_static_method:
        ft = FunctionType.STATIC_METHOD
    elif is_instance:
        ft = FunctionType.INSTANCE_METHOD
    
    description = ast.get_docstring(node)

    return FunctionSpec.create(
        name=node.name,
        return_annotation=return_annotation,
        decorators=decorators,
        parameters=params,
        suite=suite,
        function_type=ft,
        description=description,
    )

def parse_parameter_from_assign(node: ast.AnnAssign | ast.Assign) -> list[VariableSpec]:
    """Parses AnnAssign/Assign into VariableSpec list (for attributes)."""
    # Logic similar to ParameterSpec.parse_ast
    
    results = []
    
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            name = node.target.id
            anno = type_parser.parse_type(node.annotation)
            
            # Default?
            # VariableSpec has assignment field.
            # Convert node.value (AST) to AssignmentSpec?
            # We can capture the code for now.
            assignment = None
            if node.value:
                assignment = assignment_parser.parse_assignment_value(node.value)
            
            ps = VariableSpec.create(
                name=name, 
                type_spec=anno,
                assignment=assignment
            )
            results.append(ps)
            
    elif isinstance(node, ast.Assign):
         for target in node.targets:
             if isinstance(target, ast.Name):
                 # For Assign, type is inferred or absent. VariableSpec allows optional type_spec.
                 # VariableSpec(name, type_spec=None, assignment=...)
                 
                 assignment = None
                 if node.value:
                    assignment = assignment_parser.parse_assignment_value(node.value)

                 results.append(VariableSpec.create(
                     name=target.id,
                     type_spec=None, # TypeAnnotationSpec(name="Any") ? Or None.
                     assignment=assignment
                 ))
                 
    return results
