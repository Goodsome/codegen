from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.python_enum_spec import PythonEnumSpec
from codegen.python_gen.domain.services.dependency_resolver import DependencyResolver
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec

def test_resolve_enum_dependency():
    # 1. Create a ModuleSpec with an Enum
    enum_spec = PythonEnumSpec.create(
        name="UserRole",
        members=[]
    )
    module_spec = ModuleSpec.create(
        name="enums",
        enums=[enum_spec]
    )
    
    # 2. Setup PackageSpec for resolver
    package_spec = PackageSpec.create(
        name="test_package",
        modules=[module_spec]
    )
    
    # 3. Resolve dependencies
    resolver = DependencyResolver.build_from_package_spec(package_spec)
    imports = list(resolver.resolve_module(module_spec))
    
    # 4. Verify 'Enum' is in imports from 'enum' module
    enum_import = next((imp for imp in imports if imp.module == "enum"), None)
    assert enum_import is not None, "Should have an import from 'enum' module"
    assert any(n.name == "Enum" for n in enum_import.names), "Should import 'Enum'"

def test_resolve_multiple_dependencies_including_enum():
    from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
    from codegen.python_gen.domain.value_objects.variable_spec import VariableSpec
    from codegen.python_gen.domain.value_objects.type_annotation_spec import TypeAnnotationSpec

    enum_spec = PythonEnumSpec.create(name="Status")
    class_spec = ClassSpec.create(
        name="User",
        attributes=[
            VariableSpec.create(name="id", type_spec=TypeAnnotationSpec(name="UUID"))
        ]
    )
    module_spec = ModuleSpec.create(
        name="models",
        enums=[enum_spec],
        classes=[class_spec]
    )
    
    package_spec = PackageSpec.create(name="pkg", modules=[module_spec])
    resolver = DependencyResolver.build_from_package_spec(package_spec)
    imports = list(resolver.resolve_module(module_spec))
    
    modules_imported = {imp.module for imp in imports}
    assert "enum" in modules_imported
    assert "uuid" in modules_imported
