from typing import Union
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from pydantic import BaseModel, Field


class GeneratePackageCommand(BaseModel):
    package_spec: PackageSpec
    overwrite: bool = Field(default_factory=False)
    nodes: list[str] | None = Field(default=None)
