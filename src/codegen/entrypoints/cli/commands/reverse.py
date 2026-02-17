"""
Reverse command - Reverse-engineer Python code into codegen.yaml blueprint.

Replaces the old 'codegen generate-blueprint' command.
"""

from pathlib import Path

import typer
from codegen.entrypoints.cli.utils import get_container, get_default_package_path
from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprintCommand,
)

app = typer.Typer(name="reverse", help="Reverse engineer Python code to blueprint")


@app.command()
def reverse(
    config_file: str = typer.Option(
        "codegen.yaml",
        "--config",
        "-c",
        help="Path to output codegen.yaml blueprint file",
    ),
    package_path: Path | None = typer.Option(
        None,
        "--package",
        help="Path to existing Python package to reverse engineer (default: auto-detect from src/)",
    ),
):
    """
    Reverse: Reverse-engineer Python code into codegen.yaml.
    
    This command analyzes an existing Python package and generates
    a codegen.yaml blueprint that describes its structure.
    
    Examples:
        $ codegen reverse
        $ codegen reverse --package ./src/mypackage
        $ codegen reverse -c custom_blueprint.yaml
    """
    config_file_path = Path(config_file)
    with get_container(config_file=config_file_path) as container:
        if package_path is None:
            package_path = get_default_package_path()
        use_case = container.update_blueprint_use_case()
        cmd = GenerateBlueprintCommand(path=package_path)
        use_case.execute(cmd)
        typer.echo(f"Reverse engineering completed. Blueprint saved to {config_file}")
