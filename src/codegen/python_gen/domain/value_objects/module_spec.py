"""
Kind: ValueObject
Name: ModuleSpec
Description: Represents a Python module.
"""

from pydantic.fields import computed_field
import re
from pathlib import Path

from pydantic.fields import Field
from codegen.domain.shared.models import ValueObject

from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.function_spec import FunctionSpec
from codegen.python_gen.domain.value_objects.import_spec import ImportSpec


class ModuleSpec(ValueObject):
    """Represents a Python module."""

    directory: Path
    filename: str
    functions: list[FunctionSpec] = Field(default_factory=list)
    classes: list[ClassSpec] = Field(default_factory=list)
    imports: list[ImportSpec] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        directory: str | Path,
        filename: str,
        functions: list[FunctionSpec] | None = None,
        classes: list[ClassSpec] | None = None,
        imports: list[ImportSpec] | None = None,
    ) -> "ModuleSpec":
        if isinstance(directory, str):
            directory = Path(directory)
        filename = cls._to_snake_case(filename)
        if not filename.endswith(".py"):
            filename += ".py"
        return cls(
            directory=directory,
            filename=filename,
            functions=functions or [],
            classes=classes or [],
            imports=imports or [],
        )

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """内部工具：将字符串转换为 snake_case"""
        # 处理 CamelCase 或已有空格/横杠的情况
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower().replace("-", "_")

    @computed_field
    @property
    def full_path(self) -> Path:
        return self.directory / self.filename
