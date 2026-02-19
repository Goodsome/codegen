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

    def is_nullable(self) -> bool:
        """判断类型是否可为空"""
        if self.name == "None":
            return True
        if self.name == "Union" and "None" in [arg.name for arg in self.args]:
            return True
        return False

    @classmethod
    def from_raw(cls, raw_type: str) -> "TypeAnnotationSpec":
        """Creates a TypeAnnotationSpec from a raw type string.

        Args:
            raw_type: A type string like "str", "int", "list[str]", "dict[str, int]"

        Returns:
            TypeAnnotationSpec representing the type
        """
        import ast
        import re

        if not raw_type or raw_type.strip() == "":
            return cls(name="Any")

        raw_type = raw_type.strip()

        # Handle Union types with |
        if "|" in raw_type:
            parts = [p.strip() for p in raw_type.split("|")]
            if len(parts) == 2 and "None" in parts:
                # Optional type
                non_none = parts[0] if parts[1] == "None" else parts[1]
                base = cls.from_raw(non_none)
                return cls(name="Optional", args=[base])
            else:
                # General Union
                args = [cls.from_raw(p) for p in parts]
                return cls(name="Union", args=args)

        # Parse generic types like list[str], dict[str, int], etc.
        match = re.match(r"^(\w+)\[(.+)\]$", raw_type)
        if match:
            base_name = match.group(1)
            args_str = match.group(2)

            # Split args by comma, handling nested brackets
            args = []
            bracket_count = 0
            current_arg = ""
            for char in args_str:
                if char == "[":
                    bracket_count += 1
                    current_arg += char
                elif char == "]":
                    bracket_count -= 1
                    current_arg += char
                elif char == "," and bracket_count == 0:
                    args.append(current_arg.strip())
                    current_arg = ""
                else:
                    current_arg += char
            if current_arg.strip():
                args.append(current_arg.strip())

            type_args = [cls.from_raw(arg) for arg in args]
            return cls(name=base_name, args=type_args)

        # Simple type
        mapped = _TYPE_NAME_MAPPING.get(raw_type, raw_type)
        return cls(name=mapped)
