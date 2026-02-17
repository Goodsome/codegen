

from codegen.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.imported_name import ImportedName


class ImportFromSpec(ValueObject):
    """Represents an import statement from another module."""

    module: str
    names: list[ImportedName]

    @classmethod
    def create(
        cls, module: str, names: list[str]
    ) -> "ImportFromSpec":
        _names: list[ImportedName] = []
        for name in names:
            _names.append(ImportedName(name=name))
        return cls(
            module=module,
            names=_names,
        )



    def has_name(self, name: str) -> bool:
        return any(name == imported_name.name for imported_name in self.names)

    def add_name(self, name: str) -> "ImportFromSpec":
        if self.has_name(name):
            return self
        self.names.append(ImportedName(name=name))
        return self

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
        if len(self.names) == 1:
            return self.names[0].render()
        else:
            names = ", ".join(name.render() for name in self.names)
            return f"({names})"

    def merge(self, other: "ImportFromSpec") -> "ImportFromSpec":
        if self.module != other.module:
            return self
        return self.__class__(
            module=self.module,
            names=self.names + other.names,
        )
