from pathlib import Path
from src.codegen.domain.ports.file_system_port import FileSystemPort

class RealFileSystemAdapter(FileSystemPort):
    def write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def ensure_package(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        init_file = path / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")