import typer
from pathlib import Path
from typing import Optional
from codegen.bootstrap import Container
from codegen.application.use_cases.generate_code import GenerateCodeCommand

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
    container = Container()

    current_dir = Path(__file__).parent.parent  # src/codegen
    config = {
        "template_root": current_dir / "templates",
        "output_root": current_dir.parent.parent,  # Root of project
        "encoding": "utf-8",
    }
    container.config.from_dict(config)

    # 2. 获取 Handler
    handler = container.generate_code_use_case()

    # 3. 确定目标路径
    if build:
        target_path = "src/codegen"
    else:
        target_path = "target"

    # 4. 执行命令
    cmd = GenerateCodeCommand(
        overwrite=overwrite,
        node=node,
        target_path=target_path,
    )

    result = handler.execute(cmd)
    typer.echo(f"Generation Complete. {len(result.files_written)} files processed.")


if __name__ == "__main__":
    app()
