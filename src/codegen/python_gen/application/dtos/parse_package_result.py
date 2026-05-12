from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from pydantic import BaseModel


class ParsePackageResult(BaseModel):
    package_spec: PackageSpec
