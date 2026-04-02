from codegen.orchestration.domain.enums import FileStatus
from codegen.orchestration.domain.value_objects.file_result import FileResult
from codegen.shared.domain.core import ValueObject
from pydantic import ConfigDict


class BuildStats(ValueObject):
    """Aggregated statistics for a build operation."""

    model_config = ConfigDict(frozen=False)

    total_files: int = 0
    created_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    duration_ms: int = 0

    def add_result(self, result: FileResult):
        self.total_files += 1
        if result.status == FileStatus.CREATED:
            self.created_count += 1
        elif result.status == FileStatus.UPDATED:
            self.updated_count += 1
        elif result.status == FileStatus.SKIPPED:
            self.skipped_count += 1
        elif result.status == FileStatus.FAILED:
            self.failed_count += 1
