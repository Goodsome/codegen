from pathlib import Path
from typing import Optional

import typer
from codegen.cli.utils import get_container, get_default_package_path
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprintCommand,
)
from codegen.python_gen.application.use_cases.generate_schema_json import (
    GenerateSchemaJson,
    GenerateSchemaJsonCommand,
)

app = typer.Typer(name="generate", help="Generation commands")


@app.command(name="project")
def generate(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files without prompting"
    ),
    build: bool = typer.Option(
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
        help="Path to the codegen.yaml blueprint file (default: codegen.yaml in current directory)",
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        help="Custom output directory (overrides --build/--no-build default locations)",
    ),
):
    """
    Generate Python code from a codegen.yaml blueprint.
    """
    subdir = "src" if build else "target"
    with get_container(config_file=config_file, out=out, subdir=subdir) as container:
        use_case = container.generate_project_use_case()
        if node is not None:
            overwrite = True
        root_path = ""
        if out:
            root_path = str(out).replace("/", ".").replace("\\", ".")
        cmd = GenerateProjectCommand(overwrite=overwrite, node=node, root_path=root_path)
        use_case.execute(cmd)


@app.command(name="blueprint")
def generate_blueprint(
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
    Reverse engineer an existing Python package into a codegen.yaml blueprint.
    """
    config_file_path = Path(config_file)
    with get_container(config_file=config_file_path) as container:
        if package_path is None:
            package_path = get_default_package_path()
        use_case = container.update_blueprint_user_case()
        cmd = GenerateBlueprintCommand(path=package_path)
        use_case.execute(cmd)


@app.command(name="schema")
def generate_blueprint_schema():
    """
    Generate JSON schema for codegen.yaml blueprint validation.
    """
    with get_container() as container:
        use_case = GenerateSchemaJson(file_system_port=container.os_file_port())
        cmd = GenerateSchemaJsonCommand()
        use_case.execute(cmd)
