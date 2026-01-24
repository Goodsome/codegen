from codegen.shared.domain.value_objects.macro_string import MacroString
import ast
from codegen.shared.models import ValueObject
from pydantic import Field


class PythonEnumMemberSpec(ValueObject):
    """Represents an enum member in a Python module."""

    name: MacroString
    value: str | int | None = Field(default=None)
    description: str = Field(default_factory=str)

    @classmethod
    def create(
        cls, name: str, value: str | int | None = None, description: str = ""
    ) -> "PythonEnumMemberSpec":
        return cls(
            name=MacroString(name),
            value=value,
            description=description,
        )

    @classmethod
    def parse_ast(cls, node: ast.Assign | ast.AnnAssign) -> "PythonEnumMemberSpec":
        description = ""
        # 尝试获取紧跟在成员定义后的文档字符串（通常在 body 中的下一个节点）
        # 但在普通的 Assignment 中，ast 不会直接把后面的字符串作为 docstring
        # 这里简化处理，只解析 name 和 value

        name = ""
        value = None

        if isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                value = cls._parse_value(node.value)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                name = node.target.id
                if node.value:
                    value = cls._parse_value(node.value)

        return cls(name=name, value=value, description=description)

    @staticmethod
    def _parse_value(node: ast.AST) -> str | int | None:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, int)):
                return node.value
            return str(node.value)
        return ast.unparse(node)
