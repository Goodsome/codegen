"""
Kind: ValueObject
Name: TypeAnnotationSpec
Description: Represents a type annotation.
"""

from pydantic import Field

from codegen.shared.models import ValueObject

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
    args: list["TypeAnnotationSpec"] = Field(default_factory=list)

    def render(self) -> str:
        """递归渲染类型字符串"""
        if not self.args:
            return self.name
        sub_renders = [arg.render() for arg in self.args]
        if self.name == "Union" and "None" in sub_renders:
            return " | ".join(sub_renders)
        args = ", ".join(sub_renders)
        return f"{self.name}[{args}]"

    def get_all_referenced_names(self) -> set[str]:
        """递归获取所有引用的类型名称"""
        names = {self.name}
        for arg in self.args:
            names.update(arg.get_all_referenced_names())
        return names
