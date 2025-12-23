import typer
from pathlib import Path
from typing import Optional
from codegen.bootstrap import Container
from codegen.orchestration.workflows.generate_project import GenerateCodeCommand

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

    current_dir = Path(__file__).parent.parent  # src/codegen
    config = {
        "template_root": current_dir / "python_gen" / "templates",
        "output_root": current_dir.parent.parent / "target",
        "encoding": "utf-8",
    }
    container = Container(config=config)
    workflow = container.generate_code_workflow()
    cmd = GenerateCodeCommand(overwrite=overwrite, node=node)
    workflow.execute(cmd)


if __name__ == "__main__":
    app()
