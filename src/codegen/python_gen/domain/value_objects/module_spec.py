"""
Kind: ValueObject
Name: ModuleSpec
Description: Represents a Python module.
"""

from codegen.python_gen.domain.value_objects.enum_spec import EnumSpec
import ast
import re

from pydantic.fields import Field

from codegen.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec


class ModuleSpec(ValueObject):
    """Represents a Python module."""

    name: str
    functions: list[FunctionSpec] = Field(default_factory=list)
    classes: list[ClassSpec] = Field(default_factory=list)
    imports: list[ImportFromSpec] = Field(default_factory=list)
    enums: list[EnumSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        functions: list[FunctionSpec] | None = None,
        classes: list[ClassSpec] | None = None,
        imports: list[ImportFromSpec] | None = None,
        enums: list[EnumSpec] | None = None,
    ) -> "ModuleSpec":
        name = cls._to_snake_case(name)
        return cls(
            name=name,
            functions=functions or [],
            classes=classes or [],
            imports=imports or [],
            enums=enums or [],
        )

    @classmethod
    def get_init_module(cls) -> "ModuleSpec":
        return cls.create(name="__init__")

    @classmethod
    def parse_code(cls, source_code: str, module_name: str) -> "ModuleSpec":
        tree = ast.parse(source_code)
        classes: list[ClassSpec] = []
        functions: list[FunctionSpec] = []
        imports: list[ImportFromSpec] = []
        enums: list[EnumSpec] = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                if module_name == "enums":
                    enums.append(EnumSpec.parse_ast(node))
                else:
                    classes.append(ClassSpec.parse_ast(node, source_code))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(FunctionSpec.parse_ast(node, source_code))
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ImportFromSpec.parse_ast(node))
        return cls.create(
            name=module_name,
            classes=classes,
            functions=functions,
            imports=imports,
            enums=enums,
        )

    @property
    def filename(self) -> str:
        return f"{self.name}.py"

    def is_init_module(self) -> bool:
        return self.name == "__init__"

    def is_match_name(self, name: str) -> bool:
        return self.name == self._to_snake_case(name)

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """内部工具：将字符串转换为 snake_case"""
        # 处理 CamelCase 或已有空格/横杠的情况
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower().replace("-", "_")

    def get_required_types(self) -> set[str]:
        """收集本模块所有需要的类型名称"""
        types: set[str] = set()
        for cls in self.classes:
            types.update(cls.get_required_types())
        for f in self.functions:
            types.update(f.get_required_types())
        return types

    def has_class(self, class_name: str) -> bool:
        """检查模块中是否存在指定名称的类"""
        return any(cls.name == class_name for cls in self.classes)

    def has_function(self, function_name: str) -> bool:
        """检查模块中是否存在指定名称的函数"""
        return any(f.name == function_name for f in self.functions)

    def has_class_or_function(self, name: str) -> bool:
        return self.has_class(name) or self.has_function(name)

    def collect_class_spec(self) -> dict[str, ClassSpec]:
        return {c.name: c for c in self.classes}

    def merge(self, other: "ModuleSpec") -> "ModuleSpec":
        if self.name != other.name:
            return self
        other_functions = {f.name: f for f in other.functions}
        other_classes = {c.name: c for c in other.classes}
        functions: list[FunctionSpec] = []
        classes: list[ClassSpec] = []
        for f in self.functions:
            if f.name in other_functions:
                functions.append(f.merge(other_functions[f.name]))
            else:
                functions.append(f)
        for c in self.classes:
            if c.name in other_classes:
                classes.append(c.merge(other_classes[c.name]))
            else:
                classes.append(c)

        imports_bag: dict[str, ImportFromSpec] = {}
        for i in self.imports:
            if i.module in imports_bag:
                imports_bag[i.module].names.extend(i.names)
            else:
                imports_bag[i.module] = i
        for i in other.imports:
            if i.module in imports_bag:
                imports_bag[i.module].names.extend(i.names)
            else:
                imports_bag[i.module] = i
        imports = list(imports_bag.values())
        return ModuleSpec.create(
            name=self.name,
            functions=functions,
            classes=classes,
            imports=imports,
            enums=self.enums,
        )
