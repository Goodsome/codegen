from contextlib import contextmanager
from importlib import resources
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Optional

import typer

from codegen.bootstrap import Container
from codegen.orchestration.application.use_cases.generate_project import (
    GenerateProjectCommand,
)
from codegen.orchestration.application.use_cases.generate_blueprint import (
    GenerateBlueprintCommand,
)
from codegen.python_gen.application.use_cases.generate_schema_json import (
    GenerateSchemaJsonCommand,
    GenerateSchemaJson,
)
from codegen.domain_definition.application.use_cases.modify_blueprint import (
    AddComponentCommand,
    UpdateComponentCommand,
    DeleteComponentCommand,
)
from codegen.domain_definition.application.use_cases.load_blueprint import (
    LoadBlueprintCommand,
)
from codegen.shared.application.services.attribute_parser import AttributeParser
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.attribute_spec import AttributeSpec
from codegen.domain_definition.domain.value_objects.bounded_context import BoundedContext


# 创建 Typer 应用实例
app = typer.Typer(
    name="codegen",
    help="""A DDD (Domain-Driven Design) Project Scaffolding Tool.

    Codegen reads a codegen.yaml blueprint file that defines your project structure
    and generates Python code based on DDD patterns. It can also reverse-engineer
    existing Python packages back into a codegen.yaml blueprint.

    Common commands:
    - codegen generate              Generate code from codegen.yaml
    - codegen generate-blueprint    Reverse engineer Python package to blueprint
    - codegen generate-blueprint-schema  Generate JSON schema for blueprint
        

    For more information, see: https://github.com/Goodsome/codegen
    """,
    add_completion=False,
    rich_markup_mode="markdown",
    pretty_exceptions_show_locals=False,
)


def _get_version() -> str:
    try:
        return version("codegen")
    except PackageNotFoundError:
        return "0.0.0+local"


def version_callback(value: bool):
    if value:
        typer.echo(_get_version())
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    pass


@contextmanager
def get_container(
    config_file: Path = Path("codegen.yaml"),
    out: Path | None = None,
    subdir: str | None = None,
):
    cwd = Path.cwd()
    yaml_path = config_file if config_file.is_absolute() else (cwd / config_file)
    output_dir = out or (cwd / subdir if subdir else cwd)
    template_root = resources.files("codegen") / "python_gen" / "templates"

    with resources.as_file(template_root) as path:
        config = {
            "template_root": path,
            "output_root": output_dir,
            "project_root": cwd,
            "encoding": "utf-8",
            "config_path": yaml_path,
        }
        yield Container(config=config)


def get_default_package_path() -> Path:
    cwd = Path.cwd()
    src_dir = cwd / "src"
    if src_dir.exists():
        pkgs = [
            p for p in src_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
        ]
        path = pkgs[0] if pkgs else src_dir
    else:
        path = cwd
    return path


@app.command()
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

    This command reads the codegen.yaml configuration file and generates a complete
    DDD project structure including:
        - Domain layer (aggregates, value objects, services, enums, ports)
        - Application layer (use cases, commands, queries, results)
        - Infrastructure layer (adapters, implementations)

    Examples:
        codegen generate # Generate with defaults (src/ output)
        codegen generate --overwrite # Regenerate and overwrite existing files
        codegen generate --no-build --out ./output # Output to custom directory
        codegen generate --node MyContext # Generate only MyContext bounded context
        codegen generate -c my-project.yaml # Use custom config file
    """
    subdir = "src" if build else "target"
    with get_container(config_file=config_file, out=out, subdir=subdir) as container:
        use_case = container.generate_project_use_case()
        if node is not None:
            overwrite = True
        cmd = GenerateProjectCommand(overwrite=overwrite, node=node)
        use_case.execute(cmd)


@app.command(name="generate-blueprint")
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

    This command analyzes Python source code and generates a codegen.yaml file
    that describes the project structure using DDD concepts (bounded contexts,
    aggregates, value objects, ports, use cases, etc.).

    Examples:
        codegen generate-blueprint # Auto-detect package and output codegen.yaml
        codegen generate-blueprint --package ./src/myapp # Analyze specific package
        codegen generate-blueprint -c blueprint-draft.yaml # Output to custom file
    """
    config_file_path = Path(config_file)
    with get_container(config_file=config_file_path) as container:
        if package_path is None:
            package_path = get_default_package_path()
        use_case = container.update_blueprint_user_case()
        cmd = GenerateBlueprintCommand(path=package_path)
        use_case.execute(cmd)


@app.command(name="generate-blueprint-schema")
def generate_blueprint_schema():
    """
    Generate JSON schema for codegen.yaml blueprint validation.

    This creates a codegen.schema.json file that can be used with YAML editors
    (like VS Code) to enable autocomplete and validation for codegen.yaml files.
    """
    with get_container() as container:
        use_case = GenerateSchemaJson(file_system_port=container.os_file_port())
        cmd = GenerateSchemaJsonCommand()
        use_case.execute(cmd)


# Create 'add' command group
add_app = typer.Typer(name="add", help="Add components to the blueprint")
app.add_typer(add_app, name="add")


@add_app.command("context")
def add_context(
    name: str = typer.Argument(..., help="Name of the Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
):
    """Add a new Bounded Context."""
    with get_container() as container:
        use_case = container.add_component_use_case()
        context = BoundedContext.create(name=name, description=description)
        cmd = AddComponentCommand(context=name, component=context)
        use_case.execute(cmd)
    typer.echo(f"✅ Context '{name}' added.")


@add_app.command("aggregate")
def add_aggregate(
    name: str = typer.Argument(..., help="Name of the Aggregate"),
    context: str = typer.Option(..., "--context", "-c", help="Target Bounded Context"),
    description: str = typer.Option("", "--desc", "-d", help="Description"),
    attributes: list[str] = typer.Option(
        [], "--attr", "-a", help="Attributes in format 'name:type:optional'"
    ),
):
    """Add a new Aggregate."""
    with get_container() as container:
        use_case = container.add_component_use_case()
        
        parsed_attrs = []
        for attr_str in attributes:
            pa = AttributeParser.parse(attr_str)
            parsed_attrs.append(
                AttributeSpec.create(name=pa.name, type=pa.type, optional=pa.optional)
            )

        aggregate = AggregateSpec(
            name=name,  # type: ignore
            description=description,
            attributes=parsed_attrs,
        )
        cmd = AddComponentCommand(context=context, component=aggregate)
        use_case.execute(cmd)
    
    typer.echo(f"✅ Aggregate '{name}' added to context '{context}'.")


# Update command group
update_app = typer.Typer(name="update", help="Update existing components")
app.add_typer(update_app, name="update")

@update_app.command("aggregate")
def update_aggregate(
    name: str = typer.Argument(..., help="Name of the Aggregate"),
    context: str = typer.Option(..., "--context", "-c", help="Target Bounded Context"),
    description: str = typer.Option(None, "--desc", "-d", help="New Description"),
    attributes: list[str] = typer.Option(
        [], "--add-attr", "-a", help="Add attributes 'name:type'"
    ),
):
    """Update an Aggregate. Currently supports adding attributes or updating description."""
    with get_container() as container:
        # 1. Load existing blueprint
        loader = container.load_blueprint_use_case()
        res = loader.execute(LoadBlueprintCommand())
        blueprint = res.blueprint

        # 2. Find Context
        ctx_obj = blueprint.get_context(context)
        if not ctx_obj:
            typer.echo(f"❌ Context '{context}' not found.")
            raise typer.Exit(1)

        # 3. Find Aggregate
        # Note: BoundedContext doesn't map aggregates by name publicly, we search list
        found_agg = next((a for a in ctx_obj.domain.aggregates if str(a.name) == name), None)
        if not found_agg:
            typer.echo(f"❌ Aggregate '{name}' not found inside context '{context}'.")
            raise typer.Exit(1)

        # 4. Modify
        new_desc = description if description is not None else found_agg.description
        
        # Merge Attributes
        if attributes:
            # Copy existing
            final_attrs = list(found_agg.attributes)
            for attr_str in attributes:
                pa = AttributeParser.parse(attr_str)
                new_spec = AttributeSpec.create(name=pa.name, type=pa.type, optional=pa.optional)
                
                # Check existance
                idx = next((i for i, x in enumerate(final_attrs) if x.name == new_spec.name), -1)
                if idx >= 0:
                    final_attrs[idx] = new_spec # Update
                else:
                    final_attrs.append(new_spec) # Add
        else:
            final_attrs = found_agg.attributes

        new_agg = AggregateSpec(
            name=found_agg.name,
            description=new_desc,
            attributes=final_attrs,
            behaviors=found_agg.behaviors
        )

        # 5. Save (Update)
        updater = container.update_component_use_case()
        updater.execute(UpdateComponentCommand(context=context, component=new_agg))

    typer.echo(f"✅ Aggregate '{name}' updated.")

# Delete command group
delete_app = typer.Typer(name="delete", help="Delete components")
app.add_typer(delete_app, name="delete")

@delete_app.command("context")
def delete_context(
    name: str = typer.Argument(..., help="Name of the Bounded Context"),
):
    with get_container() as container:
        use_case = container.delete_component_use_case()
        cmd = DeleteComponentCommand(context="ROOT", name=name, type="context")
        use_case.execute(cmd)
    typer.echo(f"✅ Context '{name}' deleted.")

@delete_app.command("aggregate")
def delete_aggregate(
    name: str = typer.Argument(..., help="Name of the Aggregate"),
    context: str = typer.Option(..., "--context", "-c", help="Target Bounded Context"),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
):
    with get_container(config_file=config_file) as container:
        use_case = container.delete_component_use_case()
        cmd = DeleteComponentCommand(context=context, name=name, type="aggregate")
        use_case.execute(cmd)
    typer.echo(f"✅ Aggregate '{name}' deleted from context '{context}'.")



if __name__ == "__main__":
    app()
