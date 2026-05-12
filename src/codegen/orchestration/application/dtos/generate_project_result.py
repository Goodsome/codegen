from codegen.orchestration.domain.value_objects.build_result import BuildResult
from pydantic import BaseModel


class GenerateProjectResult(BaseModel):
    result: BuildResult
    tests_result: BuildResult
