
import ast
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.enums import FunctionType
from codegen.python_gen.infrastructure.adapters.ast_builders import type_builder

def build_function(func_spec: FunctionSpec) -> ast.FunctionDef | ast.AsyncFunctionDef:
    """Builds an AST FunctionDef from a FunctionSpec."""
    
    # 1. Args
    args_list = []
    defaults_list = []
    
    # Handle 'self' or 'cls' for methods if not explicit in parameters?
    # Spec says "parameters: list[ParameterSpec]".
    # Design says: "If is_instance_method(), first argument via ast.arg(arg='self')".
    # But usually ParameterSpec list in Spec *excludes* self?
    # Let's check logic. FunctionSpec.is_instance_method() logic depends on type.
    # If parameters list already has self, we shouldn't add it doubly.
    # Spec `parameters` usually excludes implicit `self` in many DDD specs, but here `FunctionSpec` might include it or not.
    # Design doc says: "If is_instance_method() is True, first parameter via ast.arg(arg='self') add."
    # Then "Iterate func_spec.parameters".
    # This implies `parameters` does NOT contain self.
    
    if func_spec.is_instance_method():
        args_list.append(ast.arg(arg="self", annotation=None))
    elif func_spec.function_type == FunctionType.CLASS_METHOD:
        args_list.append(ast.arg(arg="cls", annotation=None))
        
    for param in func_spec.parameters:
        # Build arg
        arg_node = build_parameter(param)
        args_list.append(arg_node)
        
        # Build default
        if param.default: # default is FieldSpec or None (wait, ParameterSpec says default: FieldSpec | None)
             # However FieldSpec wraps value logic.
             # render_default() gives string.
             default_str = param.render_default()
             if default_str:
                 try:
                     defaults_list.append(ast.parse(default_str, mode='eval').body)
                 except SyntaxError:
                     # Fallback to string or error?
                     defaults_list.append(ast.Constant(value=None)) 
    
    arguments = ast.arguments(
        posonlyargs=[],
        args=args_list,
        kwonlyargs=[],
        kw_defaults=[],
        defaults=defaults_list
    )
    
    # 2. Body
    body = []
    if func_spec.suite:
        try:
             # Parse suite code.
             # If suite is "return 1", ast.parse OK.
             # If suite has indentation, we need to be careful? 
             # ast.parse dedents? No. But suite usually unindented str.
             parsed_suite = ast.parse(func_spec.suite) # Module
             if parsed_suite.body:
                 body.extend(parsed_suite.body)
             else:
                 body.append(ast.Expr(value=ast.Constant(value=...)))
        except SyntaxError:
             # Fallback
             body.append(ast.Expr(value=ast.Constant(value=...)))
    else:
        body.append(ast.Expr(value=ast.Constant(value=...)))
        
    # 3. Returns
    return_annotation = type_builder.build_type_annotation(func_spec.return_annotation)
    
    # 4. Decorators
    decorator_list = []
    for d in func_spec.decorators:
        try:
            decorator_list.append(ast.parse(d, mode='eval').body)
        except SyntaxError:
            pass
            
    # Function Type (Async not supported in Spec creation per design, but let's stick to FunctionDef)
    
    return ast.FunctionDef(
        name=func_spec.name,
        args=arguments,
        body=body,
        decorator_list=decorator_list,
        returns=return_annotation,
        lineno=0
    )

def build_parameter(param_spec) -> ast.arg:
    """Builds an AST arg node."""
    annotation = type_builder.build_type_annotation(param_spec.annotation)
    return ast.arg(arg=param_spec.name, annotation=annotation)

def build_parameter_as_attribute(param_spec) -> ast.AnnAssign:
    """Builds an AST AnnAssign node (for Class Attributes)."""
    target = ast.Name(id=param_spec.name, ctx=ast.Store())
    annotation = type_builder.build_type_annotation(param_spec.annotation)
    
    value = None
    if param_spec.default:
        val_str = param_spec.render_default()
        if val_str:
            try:
                value = ast.parse(val_str, mode='eval').body
            except SyntaxError:
                pass
                
    return ast.AnnAssign(
        target=target,
        annotation=annotation,
        value=value,
        simple=1
    )
