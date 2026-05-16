from pathlib import Path
from typing import ClassVar, Protocol


class ComponentPolicy(Protocol):

    target_path: ClassVar[Path]