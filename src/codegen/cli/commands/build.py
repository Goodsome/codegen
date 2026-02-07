"""
Build command - Compile codegen.yaml into Python code.

Replaces the old 'codegen generate' command.
"""

from pathlib import Path
from typing import Optional

import typer
from codegen.cli.utils import get_container
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)

app = typer.Typer(name="build", help="Build Python code from blueprint")


@app.command()
def build(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files without prompting"
    ),
    build_dir: bool = typer.Option(
        True,
        "--build/--no-build",
        help="Output to src directory (default: --build). Use --no-build to output to target directory",
    ),
    node: Optional[str] = typer.Option(
        None,
        "--node",
        help="Generate only a specific bounded context or component by name (e.g., 'DomainDefinition')",
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        help="Custom output directory (overrides --build/--no-build default locations)",
    ),
):
    """
    Build: Compile codegen.yaml into Python code.
    
    This is the primary code generation command. It reads your blueprint
    file and generates Python code based on DDD patterns.
    
    Examples:
        $ codegen build
        $ codegen build --overwrite
        $ codegen build --node DomainDefinition
        $ codegen build --no-build --out ./generated
    """
    subdir = "src" if build_dir else "target"
    with get_container(config_file=config_file, out=out, subdir=subdir) as container:
        use_case = container.generate_project_use_case()
        if node is not None:
            overwrite = True
        root_path = ""
        if out:
            root_path = str(out).replace("/", ".").replace("\\", ".")
        cmd = GenerateProjectCommand(overwrite=overwrite, node=node, root_path=root_path)
        use_case.execute(cmd)
        typer.echo("Build completed successfully.")
