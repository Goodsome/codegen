from codegen.orchestration.domain.enums import FileStatus
from pydantic import Field
from codegen.shared.domain.core import ValueObject


class FileResult(ValueObject):
    """Represents the outcome for a single file generation."""

    path: str
    status: FileStatus
    message: str = Field(default_factory=str)
    diff: str = Field(default_factory=str)
