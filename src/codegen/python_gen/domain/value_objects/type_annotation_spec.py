"""
Kind: ValueObject
Name: TypeAnnotationSpec
Description: Represents a type annotation.
"""

import ast

from pydantic import Field

from codegen.shared.models import ValueObject

_TYPE_NAME_MAPPING: dict[str, str] = {
    "string": "str",
    "String": "str",
    "List": "list",
    "Dict": "dict",
    "Set": "set",
    "Tuple": "tuple",
}

class TypeAnnotationSpec(ValueObject):
    """Represents a type annotation."""

    name: str
    args: list["TypeAnnotationSpec"] = Field(default_factory=list)


    @classmethod
    def parse(cls, annotation: str) -> "TypeAnnotationSpec":
        """
        Parses a type hint string into a TypeAnnotationSpec object.
        Supports:
          - Simple types: "int", "str", "MyClass"
          - Generics: "List[int]", "Dict[str, Any]"
          - Union syntax (Python 3.10+): "str | None", "int | str | float"
        """
        if not annotation:
            raise ValueError("Annotation string cannot be empty")

        # 使用 ast.parse 在 eval 模式下获取表达式结构
        try:
            tree = ast.parse(annotation, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid type annotation syntax: {annotation}") from e

        return cls._parse_node(tree.body)

    @classmethod
    def parse_ast(cls, node: ast.AST | None) -> "TypeAnnotationSpec":
        if node is None:
            return cls(name="Any")
        return cls._parse_node(node)

    @classmethod
    def _parse_node(cls, node: ast.AST) -> "TypeAnnotationSpec":
        """
        Recursively parses AST nodes into TypeAnnotationSpec.
        """
        # 1. 处理基础名称 (例如: int, str, List, Any)
        if isinstance(node, ast.Name):
            # 应用类型名转换映射
            type_name = node.id
            mapped_name = _TYPE_NAME_MAPPING.get(type_name, type_name)
            return cls(name=mapped_name)

        # 2. 处理常量 (例如: None)
        # Python 3.8+ 使用 Constant, 旧版可能使用 NameConstant
        if isinstance(node, ast.Constant):
            if node.value is None:
                return cls(name="None")
            return cls(name=str(node.value))  # Fallback for other constants

        # 3. 处理泛型下标 (例如: List[int], Dict[str, int])
        if isinstance(node, ast.Subscript):
            container_spec = cls._parse_node(node.value)  # 获取容器名，如 List

            # 处理下标内容
            slice_node = node.slice

            # 处理多参数泛型，如 Dict[str, int] -> slice 是一个 Tuple
            if isinstance(slice_node, ast.Tuple):
                args_specs = [cls._parse_node(elt) for elt in slice_node.elts]
            else:
                # 单参数泛型，如 List[int]
                args_specs = [cls._parse_node(slice_node)]

            return cls(name=container_spec.name, args=args_specs)

        # 4. 处理 Python 3.10+ 的 Union 语法 (例如: str | None)
        # 在 AST 中，| 被解析为 BinOp (Binary Operator) 且 op 是 BitOr
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            left = cls._parse_node(node.left)
            right = cls._parse_node(node.right)

            # 扁平化逻辑：
            # 如果左边或右边已经是 Union，则合并它们的 args，避免出现 Union[Union[A, B], C]
            merged_args = []

            if left.name == "Union":
                merged_args.extend(left.args)
            else:
                merged_args.append(left)

            if right.name == "Union":
                merged_args.extend(right.args)
            else:
                merged_args.append(right)

            return cls(name="Union", args=merged_args)

        # 5. 处理模块属性引用 (例如: typing.List, datetime.datetime)
        if isinstance(node, ast.Attribute):
            # 递归获取完整路径，例如 "typing.List"
            value_spec = cls._parse_node(node.value)
            return cls(name=f"{value_spec.name}.{node.attr}")

        raise ValueError(f"Unsupported AST node type: {type(node)}")

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

    def is_nullable(self) -> bool:
        """判断类型是否可为空"""
        if self.name == "None":
            return True
        if self.name == "Union" and "None" in [arg.name for arg in self.args]:
            return True
        return False
