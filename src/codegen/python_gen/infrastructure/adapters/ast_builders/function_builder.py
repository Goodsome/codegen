
import ast
from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.enums import FunctionType, AssignmentFlavor
from codegen.python_gen.infrastructure.adapters.ast_builders import type_builder

def build_assignment_value(assignment: AssignmentSpec) -> ast.expr:
    """Builds an AST expression from an AssignmentSpec."""
    if not assignment:
        return ast.Constant(value=None)
        
    if assignment.code:
         try:
             return ast.parse(assignment.code, mode='eval').body
         except SyntaxError:
             pass
             
    if assignment.reference:
        try:
            return ast.parse(assignment.reference.name, mode='eval').body
        except SyntaxError:
            pass
            
    if assignment.literal:
        return ast.Constant(value=assignment.literal.value)
        
    if assignment.flavor == AssignmentFlavor.CALL and assignment.call:
        args = [build_assignment_value(arg) for arg in assignment.call.args]
        keywords = [
            ast.keyword(arg=k, value=build_assignment_value(v))
            for k, v in assignment.call.kwargs.items()
        ]
        
        # Determine func node (Name or Attribute)
        try:
            func_node = ast.parse(assignment.call.callee, mode='eval').body
        except SyntaxError:
            func_node = ast.Name(id=assignment.call.callee, ctx=ast.Load())
            
        return ast.Call(func=func_node, args=args, keywords=keywords)
        
    return ast.Constant(value=None)

def build_function(func_spec: FunctionSpec) -> ast.FunctionDef | ast.AsyncFunctionDef:
    """Builds an AST FunctionDef from a FunctionSpec."""
    
    # 1. Args
    args_list = []
    defaults_list = []
    
    if func_spec.is_instance_method():
        args_list.append(ast.arg(arg="self", annotation=None))
    elif func_spec.function_type == FunctionType.CLASS_METHOD:
        args_list.append(ast.arg(arg="cls", annotation=None))
        
    for param in func_spec.parameters:
        # Build arg
        arg_node = build_parameter(param)
        args_list.append(arg_node)
        
        # Build default from assignment
        if param.assignment: 
             defaults_list.append(build_assignment_value(param.assignment))
    
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
            
    return ast.FunctionDef(
        name=func_spec.name,
        args=arguments,
        body=body,
        decorator_list=decorator_list,
        returns=return_annotation,
        lineno=0
    )

def build_parameter(param_spec) -> ast.arg:
    """Builds an AST arg node from VariableSpec."""
    annotation = None
    if param_spec.type_spec:
        annotation = type_builder.build_type_annotation(param_spec.type_spec)
    return ast.arg(arg=param_spec.name, annotation=annotation)


def build_parameter_as_attribute(param_spec) -> ast.AnnAssign:
    """Builds an AST AnnAssign node (for Class Attributes) from VariableSpec."""
    target = ast.Name(id=param_spec.name, ctx=ast.Store())
    annotation = None
    if param_spec.type_spec:
        annotation = type_builder.build_type_annotation(param_spec.type_spec)
    
    value = None
    if param_spec.assignment:
         value = build_assignment_value(param_spec.assignment)
                
    if annotation is None:
        # If there's no annotation, we must use ast.Assign instead of ast.AnnAssign
        return ast.Assign(
            targets=[target],
            value=value,
            lineno=0
        )
        
    return ast.AnnAssign(
        target=target,
        annotation=annotation,
        value=value,
        simple=1,
        lineno=0
    )
