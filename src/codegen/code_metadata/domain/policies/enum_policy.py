from pathlib import Path
from typing import ClassVar
from pydantic import BaseModel


class EnumPolicy(BaseModel):

    target_path: ClassVar[Path] = Path("domain/enums")
    