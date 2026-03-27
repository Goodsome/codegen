"""
Reverse command - Reverse-engineer Python code into codegen.yaml blueprint.
"""
from pathlib import Path

import typer
from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprint,
    GenerateBlueprintCommand,
)
from dependency_injector.wiring import Provide, inject
from typing import Annotated


def get_default_package_path() -> Path:
    """Get default package path from src/ directory."""
    src_path = Path("src")
    if not src_path.exists():
        src_path = Path(".")
    # Find first directory with __init__.py
    for item in src_path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            return item
    return src_path


@inject
def _generate_blueprint(
    cmd: GenerateBlueprintCommand,
    use_case: GenerateBlueprint = Provide[
        "orchestration_container.generate_blueprint_use_case"
    ],
) -> None:
    return use_case.execute(cmd)


def reverse(
    package_path: Annotated[Path | None, typer.Option(
        "--package",
        help="Path to existing Python package to reverse engineer (default: auto-detect from src/)",
    )] = None,
) -> None:
    """
    Reverse: Reverse-engineer Python code into codegen.yaml.

    This command analyzes an existing Python package and generates
    a codegen.yaml blueprint that describes its structure.

    Examples:
        $ codegen reverse
        $ codegen reverse --package ./src/mypackage
    """
    if package_path is None:
        package_path = get_default_package_path()

    cmd = GenerateBlueprintCommand(path=package_path)
    _generate_blueprint(cmd)
    typer.echo("Reverse engineering completed. Blueprint saved to codegen.yaml")
