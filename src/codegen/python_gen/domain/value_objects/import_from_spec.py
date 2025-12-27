import ast

from codegen.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.imported_name import ImportedName


class ImportFromSpec(ValueObject):
    """Represents an import statement from another module."""

    module: str
    names: list[ImportedName]

    @classmethod
    def create(
        cls, module: str, names: list[str] | list[ast.alias]
    ) -> "ImportFromSpec":
        _names: list[ImportedName] = []
        for name in names:
            if isinstance(name, ast.alias):
                _names.append(ImportedName(name=name.name, alias=name.asname))
            else:
                _names.append(ImportedName(name=name))
        return cls(
            module=module,
            names=_names,
        )

    @classmethod
    def parse_ast(cls, node: ast.Import | ast.ImportFrom):
        if isinstance(node, ast.ImportFrom) and node.module:
            module = node.module
        else:
            module = "__root__"
        return cls.create(
            module=module,
            names=node.names,
        )

    def has_name(self, name: str) -> bool:
        return any(name == imported_name.name for imported_name in self.names)

    def add_name(self, name: str) -> "ImportFromSpec":
        if self.has_name(name):
            return self
        self.names.append(ImportedName(name=name))
        return self

    def render(self) -> str:
        return f"{self.render_from_expression()} import {self.render_names()}"

    def render_from_expression(self) -> str:
        if self.module == "__root__":
            return ""
        return f"from {self.module}"

    def render_names(self) -> str:
        if not self.names:
            return ""
        if len(self.names) == 1:
            return self.names[0].render()
        else:
            names = ", ".join(name.render() for name in self.names)
            return f"({names})"
