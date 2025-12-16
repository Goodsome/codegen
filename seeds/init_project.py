from dataclasses import dataclass
from pathlib import Path

DDD_DIRS = ("domain", "application", "infrastructure", "interfaces")

@dataclass(frozen=True)
class InitProjectCommand:
    target_dir: Path
    package_name: str = "codegen"
    use_src_layout: bool = True

class ProjectInitializer:
    def run(self, cmd: InitProjectCommand) -> None:
        target = cmd.target_dir.resolve()
        target.mkdir(parents=True, exist_ok=True)

        # 1) docs
        (target / "docs").mkdir(parents=True, exist_ok=True)

        # 2) src layout + python package root
        if cmd.use_src_layout:
            pkg_root = target / "src" / cmd.package_name
        else:
            pkg_root = target / cmd.package_name

        pkg_root.mkdir(parents=True, exist_ok=True)
        self._ensure_init_py(pkg_root)

        # 3) DDD layers
        for d in DDD_DIRS:
            p = pkg_root / d
            p.mkdir(parents=True, exist_ok=True)
            self._ensure_init_py(p)

    @staticmethod
    def _ensure_init_py(dir_path: Path) -> None:
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")
