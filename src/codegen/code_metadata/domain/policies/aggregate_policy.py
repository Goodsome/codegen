from pathlib import Path
from typing import ClassVar


class AggregatePolicy:

    target_path: ClassVar[Path] = Path("domain/aggreates")