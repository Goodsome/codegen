from pathlib import Path
from typing import ClassVar


class EntityPolicy:

    target_path: ClassVar[Path] = Path("domain/entities")
