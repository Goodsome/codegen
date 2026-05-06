"""
Kind: ValueObject
Name: ModuleSpec
Description: Represents a Python module.
"""

from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.domain.value_objects.snake_string import SnakeString
from codegen.python_gen.domain.value_objects.python_enum_spec import PythonEnumSpec


from pydantic.fields import Field

from codegen.shared.domain.core import ValueObject
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_from_spec import ImportFromSpec
from codegen.python_gen.domain.value_objects.module_assignment_spec import (
    ModuleAssignmentSpec,
)
from codegen.python_gen.domain.value_objects.raw_code_spec import RawCodeSpec


class ModuleSpec(ValueObject):
    """Represents a Python module."""

    name: SnakeString
    functions: list[FunctionSpec] = Field(default_factory=list)
    classes: list[ClassSpec] = Field(default_factory=list)
    imports: list[ImportFromSpec] = Field(default_factory=list)
    enums: list[PythonEnumSpec] = Field(default_factory=list)
    assignments: list[ModuleAssignmentSpec] = Field(default_factory=list)
    extra_code: list[RawCodeSpec] = Field(
        default_factory=list
    )  # 逃生舱，非极端特殊情况，不能使用

    @classmethod
    def create(
        cls,
        name: str,
        functions: list[FunctionSpec] | None = None,
        classes: list[ClassSpec] | None = None,
        imports: list[ImportFromSpec] | None = None,
        enums: list[PythonEnumSpec] | None = None,
        assignments: list[ModuleAssignmentSpec] | None = None,
        extra_code: list[RawCodeSpec] | None = None,
    ) -> "ModuleSpec":
        return cls(
            name=SnakeString(name),
            functions=functions or [],
            classes=classes or [],
            imports=imports or [],
            enums=enums or [],
            assignments=assignments or [],
            extra_code=extra_code or [],
        )

    @classmethod
    def get_init_module(cls) -> "ModuleSpec":
        return cls.create(name="__init__")

    @property
    def filename(self) -> str:
        return f"{self.name}.py"

    def is_init_module(self) -> bool:
        return self.name == "__init__"

    def is_match_name(self, name: str) -> bool:
        return self.name == SnakeString(name)

    def is_match_any_name(self, names: list[str]) -> bool:
        """Check if module name matches any of the provided names."""
        return any(self.name == SnakeString(n) for n in names)

    def get_required_types(self) -> set[str]:
        """收集本模块所有需要的类型名称"""
        types: set[str] = set()
        for cls in self.classes:
            types.update(cls.get_required_types())
        for f in self.functions:
            types.update(f.get_required_types())
        for e in self.enums:
            types.update(e.get_required_types())
        for a in self.assignments:
            types.update(a.get_required_types())
        return types

    def has_class(self, class_name: str) -> bool:
        """检查模块中是否存在指定名称的类"""
        return any(cls.name == class_name for cls in self.classes)

    def get_class(self, class_name: str) -> ClassSpec:
        """获取模块中指定名称的类，不存在则 raise error"""
        for cls in self.classes:
            if cls.name == PascalString(class_name):
                return cls
        raise ValueError(f"Class '{class_name}' not found in module '{self.name}'")

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
                imports_bag[i.module] = imports_bag[i.module].merge(i)
            else:
                imports_bag[i.module] = i
        for i in other.imports:
            if i.module in imports_bag:
                imports_bag[i.module] = imports_bag[i.module].merge(i)
            else:
                imports_bag[i.module] = i

        imports = list(imports_bag.values())

        other_assignments = {a.name: a for a in other.assignments}
        assignments: list[ModuleAssignmentSpec] = []
        for a in self.assignments:
            if a.name in other_assignments:
                # Overwrite or Keep?
                # Usually later wins or verify equality.
                # For simplicity, let's say other overrides self if present.
                assignments.append(other_assignments.pop(a.name))
            else:
                assignments.append(a)
        # Add remaining
        assignments.extend(other_assignments.values())

        extra_code = self.extra_code + other.extra_code

        return ModuleSpec.create(
            name=self.name,
            functions=functions,
            classes=classes,
            imports=imports,
            enums=self.enums,
            assignments=assignments,
            extra_code=extra_code,
        )
