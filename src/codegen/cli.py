from contextlib import contextmanager
from importlib import resources
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Optional

import typer

from codegen.bootstrap import Container
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
from codegen.orchestration.application.use_cases.update_blueprint import (
    GenerateBlueprintCommand,
)
from codegen.python_gen.application.use_cases.generate_schem_json import (
    GenerateSchemaJsonCommand,
    GenerateSchemaJsonUseCase,
)

# 创建 Typer 应用实例
app = typer.Typer(
    name="codegen", help="DDD Project Scaffolding Tool", add_completion=False
)


def _get_version() -> str:
    try:
        return version("codegen")
    except PackageNotFoundError:
        return "0.0.0+local"


def version_callback(value: bool):
    if value:
        typer.echo(_get_version())
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    pass


@contextmanager
def get_container(
    config_file: Path = Path("codegen.yaml"),
    out: Path | None = None,
    subdir: str | None = None,
):
    cwd = Path.cwd()
    yaml_path = config_file if config_file.is_absolute() else (cwd / config_file)
    output_dir = out or (cwd / subdir if subdir else cwd)
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


@app.command()
def generate(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files"
    ),
    build: bool = typer.Option(True, "--build", help="Output to src directory"),
    node: Optional[str] = typer.Option(
        None, "--node", help="Specific node name to generate"
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"), "--config", "-c", help="Path to codegen.yaml"
    ),
    out: Path | None = typer.Option(None, "--out", help="Output directory"),
):
    """
    Generate code based on the blueprint.
    """
    subdir = "src" if build else "target"
    with get_container(config_file=config_file, out=out, subdir=subdir) as container:
        use_case = container.generate_project_use_case()
        cmd = GenerateProjectCommand(overwrite=overwrite, node=node)
        use_case.execute(cmd)


@app.command(name="generate-blueprint")
def generate_blueprint(
    config_file: str = typer.Option(
        "codegen.yaml", "--config", "-c", help="Path to codegen.yaml"
    ),
    package_path: Path | None = typer.Option(None, "--package", help="Package path"),
):
    config_file_path = Path(config_file)
    with get_container(config_file=config_file_path) as container:
        if package_path is None:
            package_path = get_default_package_path()
        use_case = container.update_blueprint_user_case()
        cmd = GenerateBlueprintCommand(path=package_path)
        use_case.execute(cmd)


@app.command(name="generate-blueprint-schema")
def generate_blueprint_schema():
    """
    Generate blueprint schema JSON file.
    """
    with get_container() as container:
        use_case = GenerateSchemaJsonUseCase(file_system_port=container.os_file_port())
        cmd = GenerateSchemaJsonCommand()
        use_case.execute(cmd)


if __name__ == "__main__":
    app()
