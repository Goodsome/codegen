from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
import typer
from pathlib import Path
from typing import Optional
from codegen.bootstrap import Container
from importlib import resources

# 创建 Typer 应用实例
app = typer.Typer(
    name="codegen", help="DDD Project Scaffolding Tool", add_completion=False
)


@app.command()
def generate(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files"
    ),
    build: bool = typer.Option(False, "--build", help="Build project"),
    node: Optional[str] = typer.Option(
        None, "--node", help="Specific node name to generate"
    ),
    config_file: Path = typer.Option(Path("codegen.yaml"), "--config", "-c", help="Path to codegen.yaml"),
    out: Path | None = typer.Option(None, "--out", help="Output directory"),
):
    """
    Generate code based on the blueprint.
    """
    # 1. 初始化容器并加载配置

    cwd = Path.cwd()
    yaml_path = config_file if config_file.is_absolute() else (cwd / config_file)
    target_dir = out or (cwd / ("src" if build else "target"))
    template_root = resources.files("codegen") / "python_gen" / "templates"
    config = {
        "template_root": Path(template_root),
        "output_root": target_dir,
        "encoding": "utf-8",
        "config_path": yaml_path,
    }
    container = Container(config=config)
    use_case = container.generate_project_use_case()
    cmd = GenerateProjectCommand(overwrite=overwrite, node=node)
    use_case.execute(cmd)


if __name__ == "__main__":
    app()
