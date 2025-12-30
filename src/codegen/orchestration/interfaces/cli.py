from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
import typer
from pathlib import Path
from typing import Optional
from codegen.bootstrap import Container

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
):
    """
    Generate code based on the blueprint.
    """
    # 1. 初始化容器并加载配置

    target = "src" if build else "target"
    current_dir = Path(__file__).parent.parent  # src/codegen
    config = {
        "template_root": current_dir / "python_gen" / "templates",
        "output_root": current_dir.parent.parent / target,
        "encoding": "utf-8",
    }
    container = Container(config=config)
    use_case = container.generate_project_use_case()
    cmd = GenerateProjectCommand(overwrite=overwrite, node=node)
    use_case.execute(cmd)


if __name__ == "__main__":
    app()
