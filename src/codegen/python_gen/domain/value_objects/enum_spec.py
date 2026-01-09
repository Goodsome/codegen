import ast
from codegen.shared.models import ValueObject
from pydantic import Field
from codegen.python_gen.domain.value_objects.enum_member_spec import (
    PythonEnumMemberSpec,
)


class PythonEnumSpec(ValueObject):
    """Represents an enum in a Python module."""

    name: str
    description: str = Field(default_factory=str)
    decorators: list[str] = Field(default_factory=list)
    base_class: str = Field(default_factory=str)
    members: list[PythonEnumMemberSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        decorators: list[str] | None = None,
        base_class: str = "Enum",
        members: list[PythonEnumMemberSpec] | None = None,
    ) -> "PythonEnumSpec":
        return cls(
            name=name,
            description=description,
            decorators=decorators or [],
            base_class=base_class,
            members=members or [],
        )

    @classmethod
    def parse_ast(cls, node: ast.ClassDef) -> "PythonEnumSpec":
        name = node.name
        description = ast.get_docstring(node) or ""
        decorators = [ast.unparse(decorator) for decorator in node.decorator_list]
        base_class = "Enum"
        if node.bases:
            base_class = ast.unparse(node.bases[0])

        members = []
        for item in node.body:
            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                # 检查是否为枚举成员（排除文档字符串）
                # 在 Enum 中，几乎所有的类级赋值都是成员
                # 除非它是像 __doc__ 这样的特殊属性
                if isinstance(item, ast.Assign):
                    targets = item.targets
                else:
                    targets = [item.target]

                is_member = True
                for target in targets:
                    if isinstance(target, ast.Name) and target.id.startswith("__"):
                        is_member = False
                        break

                if is_member:
                    members.append(PythonEnumMemberSpec.parse_ast(item))

        return cls.create(
            name=name,
            description=description,
            decorators=decorators,
            base_class=base_class,
            members=members,
        )
