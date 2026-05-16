from pathlib import Path
from typing import ClassVar


class ValueObjectPolicy:

    target_path: ClassVar[Path] = Path("domain/value_objects")
