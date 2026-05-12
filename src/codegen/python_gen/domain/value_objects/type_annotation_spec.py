"""
Kind: ValueObject
Name: TypeAnnotationSpec
Description: Represents a type annotation.
"""

from typing import TYPE_CHECKING

from pydantic import Field

from codegen.shared.domain.core import ValueObject

if TYPE_CHECKING:
    from codegen.python_gen.domain.value_objects.assignment_spec import AssignmentSpec

_TYPE_NAME_MAPPING: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "String": "str",
    "List": "list",
    "Dict": "dict",
    "Set": "set",
    "Tuple": "tuple",
    "void": "None",
    "boolean": "bool",
}


class TypeAnnotationSpec(ValueObject):
    """Represents a type annotation."""

    name: str
    args: list["TypeAnnotationSpec | AssignmentSpec"] = Field(default_factory=list)

    def render(self) -> str:
        """递归渲染类型字符串"""
        if not self.args:
            return self.name
        sub_renders = []
        for arg in self.args:
            if isinstance(arg, TypeAnnotationSpec):
                sub_renders.append(arg.render())
            # For AssignmentSpec (e.g., typer.Argument(...)), skip during render
        if self.name == "Union":
            return " | ".join(sub_renders)
        args = ", ".join(sub_renders)
        return f"{self.name}[{args}]"

    def get_all_referenced_names(self) -> set[str]:
        """递归获取所有引用的类型名称"""
        names: set[str] = set()
        if self.name != "Union":
            names.add(self.name)
        for arg in self.args:
            if isinstance(arg, TypeAnnotationSpec):
                names.update(arg.get_all_referenced_names())
            # AssignmentSpec items are skipped (e.g., typer.Argument(...))
        return names
