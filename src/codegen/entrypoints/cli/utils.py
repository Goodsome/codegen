from contextlib import contextmanager
from importlib import resources
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
def get_container(
    config_file: Path = Path("codegen.yaml"),
    output: str = "src",
):
    """
    Create a configured container instance.

    Args:
        config_file: Path to codegen.yaml (relative to cwd or absolute)
        output: Output directory - "src" (default) or custom path (relative to cwd or absolute)
    """
    cwd = Path.cwd()
    yaml_path = config_file if config_file.is_absolute() else (cwd / config_file)

    # Resolve output directory
    if output == "src":
        output_dir = cwd / "src"
    else:
        output_path = Path(output)
        output_dir = output_path if output_path.is_absolute() else (cwd / output_path)

    template_root = resources.files("codegen") / "python_gen" / "templates"

    with resources.as_file(template_root) as path:
        config = {
            "template_root": path,
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
