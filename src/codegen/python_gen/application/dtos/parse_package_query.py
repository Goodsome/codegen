from pathlib import Path
from pydantic import BaseModel


class ParsePackageQuery(BaseModel):
    package_path: Path
