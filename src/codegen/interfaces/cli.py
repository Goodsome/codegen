from pathlib import Path
from typing import Annotated

import typer

from codegen.application.use_cases.generate_action import GenerateActionHandler, GenerateActionCommand
from codegen.application.use_cases.init_project import InitProjectCommand, InitProjectHandler
from codegen.shared.enums import ActionKind, CodeForm
from codegen.infrastructure.adapters.jinja_adapter import JinjaTemplateAdapter
from codegen.infrastructure.adapters.os_file_system import RealFileSystemAdapter

# 创建 Typer 应用实例
app = typer.Typer(
    name="codegen",
    help="DDD Project Scaffolding Tool",
    add_completion=False
)

# --- 辅助函数 (原 _calc_project_pkg_dir 逻辑) ---
def _resolve_project_root(target: Path, package: str, no_src: bool) -> Path:
    """计算业务代码的根目录位置"""
    base = target.resolve()
    if no_src:
        return base / package
    return base / "src" / package

# --- Command: Init ---
@app.command("init")
def init_project(
        package: Annotated[str, typer.Option("--package", "-p", help="Business project's Python package name")],
        target: Annotated[Path, typer.Option("--target", "-t", help="Target directory")] = Path("."),
        no_src: Annotated[bool, typer.Option("--no-src", help="Do not use src layout")] = False,
):
    """
    Initialize a new DDD project structure.
    """
    typer.echo(f"Initializing project '{package}' in {target}...")

    cmd = InitProjectCommand(
        target_dir=target,
        package_name=package,
        use_src_layout=not no_src,
    )

    fs = RealFileSystemAdapter()
    InitProjectHandler(fs).execute(cmd)

    typer.secho(f"✨ Project structure created successfully!", fg=typer.colors.GREEN)

# --- Command: Gen ---
@app.command("gen")
def generate_action(
        kind: Annotated[ActionKind, typer.Argument(help="The type of action to generate")],
        name: Annotated[str, typer.Argument(help="snake_case name, e.g. create_user")],
        package: Annotated[str, typer.Option("--package", "-p", help="Business project's Python package name")],
        target: Annotated[Path, typer.Option("--target", "-t", help="Target project root directory")] = Path("."),
        form: Annotated[CodeForm, typer.Option(help="Generate single file or package directory")] = CodeForm.single,
        with_mapper: Annotated[bool, typer.Option(help="Generate optional mapper")] = False,
        no_src: Annotated[bool, typer.Option("--no-src", help="Do not use src layout")] = False,
):
    """
    Generate Application Actions (Use Cases or Queries).
    """
    repo_root = Path(__file__).resolve().parents[1]
    template_dir = repo_root / "templates"

    templater = JinjaTemplateAdapter(template_dir)
    fs = RealFileSystemAdapter()

    handler = GenerateActionHandler(templater, fs)
    project_pkg_dir = _resolve_project_root(target, package, no_src)
    cmd = GenerateActionCommand(
        kind=kind,
        name=name,
        target_root=project_pkg_dir,
        form=form,
        with_mapper=with_mapper,
    )

    # 3. 调用 Application Service
    try:
        output_path = handler.execute(cmd).path

        # 4. 友好的输出
        typer.secho(f"Generated {kind.value}: {name}", fg=typer.colors.BLUE)
        typer.echo(f"Location: {output_path}")
        typer.secho("✨ Done!", fg=typer.colors.GREEN)

    except ValueError as e:
        typer.secho(f"Validation Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Unexpected Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()