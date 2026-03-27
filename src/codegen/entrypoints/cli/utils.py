from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import typer
from codegen.bootstrap import Container

def _get_version() -> str:
    try:
        return version("codegen")
    except PackageNotFoundError:
        return "0.0.0+local"


def version_callback(value: bool):
    if value:
        typer.echo(_get_version())
        raise typer.Exit()


@contextmanager
def get_container():
    """
    Create a configured container instance.
    """
    cwd = Path.cwd()
    yaml_path = cwd / "codegen.yaml"
    output_dir = cwd / "src"

    config = {
        "output_root": output_dir,
        "project_root": cwd,
        "encoding": "utf-8",
        "config_path": yaml_path,
    }
    yield Container(config=config)


def get_default_package_path() -> Path:
    cwd = Path.cwd()
    src_dir = cwd / "src"
    if src_dir.exists():
        pkgs = [
            p for p in src_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
        ]
        path = pkgs[0] if pkgs else src_dir
    else:
        path = cwd
    return path
