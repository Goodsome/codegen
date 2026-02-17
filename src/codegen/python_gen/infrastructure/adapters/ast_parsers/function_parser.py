
import ast
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.parameter_spec import ParameterSpec
from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec
from codegen.python_gen.infrastructure.adapters.ast_parsers import type_parser
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
    function_type = "function" # enum value string? No, use Enum.
    # To avoid importing Domain Enum, we can perform checks.
    # But FunctionSpec expects FunctionType enum.
    # We should import it.
    
    # Wait, simple detection:
    is_class_method = any("classmethod" in d for d in decorators)
    is_static_method = any("staticmethod" in d for d in decorators)
    is_instance = not is_class_method and not is_static_method and first_arg_name == "self"
    
    # Filter args
    clean_args = node.args.args
    if is_instance or is_class_method:
        clean_args = clean_args[1:] # Drop first arg
        
    for arg in clean_args:
        # Default value?
        # defaults list aligns with end of args.
        # This mapping is tedious to do manually.
        # But we need to do it to create ParameterSpec correctly if it has default.
        # ParameterSpec currently has default: FieldSpec/None.
        # Parsing default value from AST to FieldSpec is hard without knowing context (Pydantic Field vs simple value).
        # FunctionSpec.parse_ast seemed to simplify this or delegate.
        # For now, let's implement basic parameter parsing: name + annotation.
        
        # NOTE: Current ParameterSpec.parse_ast (in Domain) only handles AnnAssign/Assign attributes, NOT function args!
        # FunctionSpec.parse_ast (in Domain) handles function args but just name + annotation.
        # It ignores defaults!
        # "params.append(ParameterSpec.create(name=arg.arg, annotation=anno))"
        # So we will follow that status quo for now.
        
        anno = type_parser.parse_type(arg.annotation)
        params.append(ParameterSpec.create(name=arg.arg, annotation=anno))

    # 2. Return Type
    return_annotation = type_parser.parse_type(node.returns)
    
    # 3. Suite
    suite = ""
    if node.body:
         # unparse body list
         suite = "\n".join([ast.unparse(b) for b in node.body])

    # 4. Create Spec
    # Need to map to FunctionType enum.
    from codegen.python_gen.domain.enums import FunctionType
    ft = FunctionType.FUNCTION
    if is_class_method: ft = FunctionType.CLASS_METHOD
    elif is_static_method: ft = FunctionType.STATIC_METHOD
    elif is_instance: ft = FunctionType.INSTANCE_METHOD
    
    is_private = node.name.startswith("_") and not node.name.startswith("__")
    
    return FunctionSpec.create(
        name=node.name,
        return_annotation=return_annotation,
        decorators=decorators,
        parameters=params,
        suite=suite,
        function_type=ft,
        is_private=is_private
    )

def parse_parameter_from_assign(node: ast.AnnAssign | ast.Assign) -> list[ParameterSpec]:
    """Parses AnnAssign/Assign into ParameterSpec list (for attributes)."""
    # Logic similar to ParameterSpec.parse_ast
    
    results = []
    
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            name = node.target.id
            anno = type_parser.parse_type(node.annotation)
            
            # Default?
            default_flavor = None # how to detect?
            # parse value...
            
            ps = ParameterSpec.create(
                name=name, 
                annotation=anno,
                optional=(node.value is not None)
            )
            # If value exists, we might want to capture it in 'default' FieldSpec.
            if node.value:
                # We can't easily reverse engineer FieldSpec from arbitrary AST yet without logic.
                pass
            results.append(ps)
            
    elif isinstance(node, ast.Assign):
         for target in node.targets:
             if isinstance(target, ast.Name):
                 results.append(ParameterSpec.create(
                     name=target.id,
                     annotation=TypeAnnotationSpec(name="Any") # inferred
                 ))
                 
    return results
