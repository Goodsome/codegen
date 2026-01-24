"""
Kind: Aggregate
Name: PackageSpec
Description: Represents a Python package.
"""

from codegen.shared.domain.value_objects.snake_string import SnakeString
from pathlib import Path

from pydantic import Field

from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.shared.models import ValueObject
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec


class PackageSpec(ValueObject):
    """Represents a Python package."""

    name: SnakeString
    modules: list[ModuleSpec] = Field(default_factory=list)
    sub_packages: list["PackageSpec"] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        modules: list[ModuleSpec] | None = None,
        sub_packages: list["PackageSpec"] | None = None,
    ):
        if modules is None:
            modules = []
        if sub_packages is None:
            sub_packages = []
        has_init_module = any(mod.is_init_module() for mod in modules)
        if not has_init_module:
            modules.append(ModuleSpec.get_init_module())
        if isinstance(name, str):
            name = SnakeString(name)
        return cls(
            name=name,
            modules=modules,
            sub_packages=sub_packages,
        )

    def is_empty(self) -> bool:
        for pkg in self.sub_packages:
            if not pkg.is_empty():
                return False
        for mod in self.modules:
            if not mod.is_init_module():
                return False
        return True

    def get_global_registry(self, root_name: str = "") -> dict[str, str]:
        symbol_table: dict[str, str] = {}
        self._build_symbol_table(root_name, symbol_table)
        return symbol_table

    def _build_symbol_table(self, root_path: str, table: dict[str, str]):
        """递归扫描所有模块，记录每个类属于哪个绝对路径"""
        if root_path:
            current_path = f"{root_path}.{self.name}"
        else:
            current_path = self.name

        for mod in self.modules:
            mod_name = Path(mod.filename).stem
            full_mod_path = f"{current_path}.{mod_name}"
            for cls in mod.classes:
                table[cls.name] = full_mod_path
            for enum in mod.enums:
                table[enum.name] = full_mod_path

        for pkg in self.sub_packages:
            pkg._build_symbol_table(current_path, table)

    def collect_class_spec(self) -> dict[str, ClassSpec]:
        result: dict[str, ClassSpec] = {}
        for mod in self.modules:
            result.update(mod.collect_class_spec())
        for pkg in self.sub_packages:
            result.update(pkg.collect_class_spec())
        return result

    def merge(self, other: "PackageSpec") -> "PackageSpec":
        if self.name != other.name:
            return self
        other_modules = {m.name: m for m in other.modules}
        other_sub_packages = {p.name: p for p in other.sub_packages}
        modules: list[ModuleSpec] = []
        sub_packages: list["PackageSpec"] = []
        for mod in self.modules:
            if mod.name in other_modules:
                new_mod = mod.merge(other_modules[mod.name])
                modules.append(new_mod)
            else:
                modules.append(mod)
        for pkg in self.sub_packages:
            if pkg.name in other_sub_packages:
                new_pkg = pkg.merge(other_sub_packages[pkg.name])
                sub_packages.append(new_pkg)
            else:
                sub_packages.append(pkg)
        return PackageSpec.create(
            name=self.name, modules=modules, sub_packages=sub_packages
        )
