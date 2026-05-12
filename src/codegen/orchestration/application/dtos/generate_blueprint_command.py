from pathlib import Path
from pydantic import BaseModel


class GenerateBlueprintCommand(BaseModel):
    path: Path
    test_path: Path = Path("tests")
