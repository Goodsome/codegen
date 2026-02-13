from codegen.orchestration.domain.enums import BuildStatus, FileStatus
from codegen.orchestration.domain.value_objects.build_stats import BuildStats
from codegen.orchestration.domain.value_objects.file_result import FileResult
from codegen.shared.models import ValueObject
from pydantic import Field, ConfigDict


class BuildResult(ValueObject):
    """Top-level result object returned by generation use cases."""

    model_config = ConfigDict(frozen=False)

    status: BuildStatus
    files: list[FileResult] = Field(default_factory=list)
    stats: BuildStats = Field(default_factory=BuildStats)
    messages: list[str] = Field(default_factory=list)

    def add_file_result(self, result: FileResult):
        if not result.status == FileStatus.SKIPPED:
            self.files.append(result)
        self.stats.add_result(result)
        if result.status == FileStatus.FAILED:
            self.status = BuildStatus.WARNING

