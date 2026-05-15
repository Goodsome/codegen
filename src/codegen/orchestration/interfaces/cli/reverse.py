"""
Reverse command - Reverse-engineer Python code into codegen.yaml blueprint.
"""
from pathlib import Path

import typer
from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprint,
    GenerateBlueprintCommand,
    GenerateBlueprintResult,
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
        "orchestration_container.generate_blueprint"
    ],
) -> GenerateBlueprintResult:
    return use_case.execute(cmd)


def reverse(
    package_path: Annotated[Path | None, typer.Option(
        "--package",
        help="Path to existing Python package to reverse engineer (default: auto-detect from src/)",
    )] = None,
    context: Annotated[str | None, typer.Option(
        "--context",
        help="Context to use for reverse engineering",
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

    cmd = GenerateBlueprintCommand(path=package_path, context=context)
    _generate_blueprint(cmd)
    typer.echo("Reverse engineering completed. Blueprint saved to codegen.yaml")
