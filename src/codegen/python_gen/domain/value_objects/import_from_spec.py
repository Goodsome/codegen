from typing import Iterable

from codegen.shared.domain.core import ValueObject
from codegen.python_gen.domain.value_objects.imported_name import ImportedName


class ImportFromSpec(ValueObject):
    """Represents an import statement from another module."""

    module: str
    names: frozenset[ImportedName]

    type_checking: bool = False
    level: int = 0  # 0 = absolute, 1 = from ., 2 = from .., etc.

    @classmethod
    def create(
        cls,
        module: str,
        names: Iterable[str],
        type_checking: bool = False,
        level: int = 0,
    ) -> "ImportFromSpec":
        _names = frozenset(ImportedName(name=name) for name in names)
        return cls(
            module=module,
            names=_names,
            type_checking=type_checking,
            level=level,
        )

    def has_name(self, name: str) -> bool:
        return any(name == imported_name.name for imported_name in self.names)

    def add_name(self, name: str) -> "ImportFromSpec":
        if self.has_name(name):
            return self
        new_names = self.names | frozenset({ImportedName(name=name)})
        return self.__class__(
            module=self.module,
            names=new_names,
            type_checking=self.type_checking,
            level=self.level,
        )

    def render(self) -> str:
        from_expr = self.render_from_expression()
        r = ""
        if from_expr:
            r = f"{from_expr} import {self.render_names()}"
        elif self.module == "__root__":
            for imported_name in self.names:
                r += f"import {imported_name.render()}\n"
        return r

    def render_from_expression(self) -> str:
        if self.module == "__root__":
            return ""
        return f"from {self.module}"

    def render_names(self) -> str:
        if not self.names:
            return ""
        sorted_names = sorted(self.names, key=lambda n: n.name)
        if len(sorted_names) == 1:
            return sorted_names[0].render()
        else:
            names = ", ".join(name.render() for name in sorted_names)
            return f"({names})"

    def merge(self, other: "ImportFromSpec") -> "ImportFromSpec":
        if self.module != other.module or self.type_checking != other.type_checking:
            return self
        return self.__class__(
            module=self.module,
            names=self.names | other.names,
            type_checking=self.type_checking,
            level=self.level,
        )
