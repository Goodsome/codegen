from codegen.orchestration.application.use_cases.update_blueprint import (
    UpdateBlueprintCommand,
)
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
import typer
from pathlib import Path
from typing import Optional
from codegen.bootstrap import Container
from importlib import resources

from contextlib import contextmanager

# 创建 Typer 应用实例
app = typer.Typer(
    name="codegen", help="DDD Project Scaffolding Tool", add_completion=False
)


@contextmanager
def get_container(
    config_file: Path = Path("codegen.yaml"),
    out: Path | None = None,
    build: bool = False,
):
    cwd = Path.cwd()
    yaml_path = config_file if config_file.is_absolute() else (cwd / config_file)
    target_dir = out or (cwd / ("src" if build else "target"))
    template_root = resources.files("codegen") / "python_gen" / "templates"

    with resources.as_file(template_root) as path:
        config = {
            "template_root": path,
            "output_root": target_dir,
            "project_root": cwd,
            "encoding": "utf-8",
            "config_path": yaml_path,
        }
        yield Container(config=config)

def get_default_package_path() -> Path:
    cwd = Path.cwd()
    src_dir = cwd / "src"
    if src_dir.exists():
        pkgs = [p for p in src_dir.iterdir() if p.is_dir() and not p.name.startswith(".")] 
        path = pkgs[0] if pkgs else src_dir
    else:
        path = cwd
    return path

@app.command()
def generate(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files"
    ),
    build: bool = typer.Option(False, "--build", help="Build project"),
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
    with get_container(config_file=config_file, out=out, build=build) as container:
        use_case = container.generate_project_use_case()
        cmd = GenerateProjectCommand(overwrite=overwrite, node=node)
        use_case.execute(cmd)


@app.command(name="update-blueprint")
def update_blueprint(
    config_file: Path = typer.Option(
        Path("codegen.yaml"), "--config", "-c", help="Path to codegen.yaml"
    ),
    package_path: Path | None = typer.Option(None, "--package", help="Package path"),
):
    with get_container(config_file=config_file, build=True) as container:
        if package_path is None:
            package_path = get_default_package_path()
        use_case = container.update_blueprint_user_case()
        cmd = UpdateBlueprintCommand(path=package_path)
        use_case.execute(cmd)


if __name__ == "__main__":
    app()
