from pathlib import Path
from unittest.mock import MagicMock
from codegen.python_gen.domain.services.python_syntax_translator import PythonSyntaxTranslator
from codegen.shared.domain.ports.template_port import TemplatePort

def test_to_package_spec():
    # Arrange
    template_port = MagicMock(spec=TemplatePort)
    translator = PythonSyntaxTranslator(template_port=template_port)
    
    source_code_tree = {
        Path("__init__.py"): "class A: pass",
        Path("module_a.py"): "def func_a(): pass",
        Path("subpkg/__init__.py"): "",
        Path("subpkg/module_b.py"): "class B: pass",
    }
    
    # Act
    package_spec = translator.to_package_spec(source_code_tree, "root_pkg")
    
    # Assert
    assert package_spec.name == "root_pkg"
    
    # Check modules in root_pkg
    # PackageSpec.create adds __init__ if missing, but we have it.
    # Actually ModuleSpec.parse_code is used.
    module_names = {m.name for m in package_spec.modules}
    assert "__init__" in module_names
    assert "module_a" in module_names
    
    # Check sub-packages
    assert len(package_spec.sub_packages) == 1
    sub_pkg = package_spec.sub_packages[0]
    assert sub_pkg.name == "subpkg"
    
    sub_module_names = {m.name for m in sub_pkg.modules}
    assert "__init__" in sub_module_names
    assert "module_b" in sub_module_names

    # Verify content of one module
    module_b = next(m for m in sub_pkg.modules if m.name == "module_b")
    assert len(module_b.classes) == 1
    assert module_b.classes[0].name == "B"
