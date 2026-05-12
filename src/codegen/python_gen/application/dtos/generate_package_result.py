from codegen.orchestration.domain.value_objects.build_result import BuildResult
from pydantic import BaseModel


class GeneratePackageResult(BaseModel):
    result: BuildResult
