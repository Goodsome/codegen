
import ast
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.infrastructure.adapters.ast_builders import function_builder

def build_class(class_spec: ClassSpec) -> ast.ClassDef:
    """Builds an AST ClassDef from a ClassSpec."""
    
    body: list[ast.stmt] = []
    
    # 1. Docstring
    if class_spec.description:
        body.append(ast.Expr(value=ast.Constant(value=class_spec.description)))
        
    # 2. Attributes
    for attr in class_spec.attributes:
        ann_assign = function_builder.build_parameter_as_attribute(attr)
        body.append(ann_assign)
        
    # 3. Methods
    for method in class_spec.methods:
        func_def = function_builder.build_function(method)
        body.append(func_def)
        
    if not body:
        body.append(ast.Expr(value=ast.Constant(value=...)))
        
    # 4. Bases
    bases = []
    for base in class_spec.inheritance:
        try:
            bases.append(ast.parse(base, mode='eval').body)
        except SyntaxError:
            bases.append(ast.Name(id=base, ctx=ast.Load()))
            
    # 5. Decorators
    decorator_list = []
    for d in class_spec.decorators:
        try:
            decorator_list.append(ast.parse(d, mode='eval').body)
        except SyntaxError:
            pass

    return ast.ClassDef(
        name=class_spec.name,
        bases=bases,
        keywords=[],
        body=body,
        decorator_list=decorator_list
    )
