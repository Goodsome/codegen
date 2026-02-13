from enum import Enum


class BuildStatus(Enum):

    SUCCESS = "SUCCESS"

    FAILURE = "FAILURE"

    WARNING = "WARNING"


class FileStatus(Enum):

    CREATED = "CREATED"

    UPDATED = "UPDATED"

    SKIPPED = "SKIPPED"

    FAILED = "FAILED"
