"""
Kind: Aggregate
Name: PackageSpec
Description: Represents a Python package.
"""

from pathlib import Path

from pydantic import Field

from codegen.domain.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec


class PackageSpec(ValueObject):
    """Represents a Python package."""

    path: Path
    modules: list[ModuleSpec] = Field(default_factory=list)
    packages: list["PackageSpec"] = Field(default_factory=list)

    def has_init_file(self) -> bool:
        """检查包是否已存在 __init__.py 文件"""
        init_file_path = self.path / "__init__.py"
        return init_file_path.exists()
