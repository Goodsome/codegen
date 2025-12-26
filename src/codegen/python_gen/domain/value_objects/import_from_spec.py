from codegen.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.imported_name import ImportedName


class ImportFromSpec(ValueObject):
    """Represents an import statement from another module."""

    module: str
    names: list[ImportedName]

    def has_name(self, name: str) -> bool:
        return any(name == imported_name.name for imported_name in self.names)

    def add_name(self, name: str) -> "ImportFromSpec":
        if self.has_name(name):
            return self
        self.names.append(ImportedName(name=name))
        return self

    def render_names(self) -> str:
        if not self.names:
            return ""
        if len(self.names) == 1:
            return self.names[0].render()
        else:
            return ", ".join(name.render() for name in self.names)
