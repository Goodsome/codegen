import unittest
from pathlib import Path
from unittest.mock import Mock

from codegen.python_gen.domain.services.python_syntax_translator import PythonSyntaxTranslator
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.shared.domain.ports.file_system_port import FileSystemPort
from codegen.python_gen.domain.ports.source_code_port import SourceCodePort


class TestPythonSyntaxTranslator(unittest.TestCase):
    def setUp(self):
        self.mock_source_code_port = Mock(spec=SourceCodePort)
        self.mock_file_system_port = Mock(spec=FileSystemPort)
        self.translator = PythonSyntaxTranslator(
            source_code_port=self.mock_source_code_port,
            file_system_port=self.mock_file_system_port
        )

    def test_to_code(self):
        # Setup
        module_spec = ModuleSpec.create(name="test_module")
        imports = [ImportFromSpec.create(module="typing", names=["List"])]
        
        self.mock_source_code_port.render_module.return_value = "rendered code"

        # Execute
        result = self.translator.to_code(module_spec, imports)

        # Assert
        self.assertEqual(result, "rendered code")
        self.mock_source_code_port.render_module.assert_called_once_with(module_spec, imports)

    def test_to_package_spec(self):
        # Setup
        package_path = Path("/tmp/test_package")
        self.mock_file_system_port.is_directory.side_effect = lambda p: p == package_path or p == package_path / "subpkg"
        self.mock_file_system_port.is_file.side_effect = lambda p: p.suffix == ".py"
        
        # Mock file system structure
        self.mock_file_system_port.list_directory_flat.side_effect = [
            [package_path / "__init__.py", package_path / "module1.py", package_path / "subpkg"], # Root contents
            [package_path / "subpkg" / "__init__.py"] # Subpkg contents
        ]
        
        self.mock_file_system_port.read_file.side_effect = [
            "init_code", # __init__.py content
            "module1_code", # module1.py content
            "subpkg_init_code" # subpkg/__init__.py content
        ]

        # Mock SourceCodePort behavior
        def side_effect_parse(source, name):
            return ModuleSpec.create(name=name)

        self.mock_source_code_port.parse_module.side_effect = side_effect_parse

        # Execute
        result = self.translator.to_package_spec(package_path)

        # Assert
        self.assertIsInstance(result, PackageSpec)
        self.assertEqual(result.name, "test_package")
        
        # Check files in root
        module_names = {m.name for m in result.modules}
        self.assertIn("__init__", module_names)
        self.assertIn("module1", module_names)
        
        # Check subpackages
        self.assertEqual(len(result.sub_packages), 1)
        subpkg = result.sub_packages[0]
        self.assertEqual(subpkg.name, "subpkg")
        self.assertTrue(any(m.name == "__init__" for m in subpkg.modules))

        # Verify calls to parse_module - call count is verified since order may vary
        self.assertEqual(self.mock_source_code_port.parse_module.call_count, 3)

    def test_to_package_spec_not_directory(self):
        # Setup
        path = Path("/tmp/file.py")
        self.mock_file_system_port.is_directory.return_value = False

        # Execute & Assert
        with self.assertRaises(ValueError):
            self.translator.to_package_spec(path)
