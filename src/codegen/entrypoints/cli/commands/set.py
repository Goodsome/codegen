"""
Set command - Set or update a value in blueprint by path.

New path-based command for modifying blueprint values.
Supports JSON values and --append mode for lists.
"""

import json
from pathlib import Path
from typing import Optional, List

import typer
from codegen.entrypoints.cli.utils import get_container
from codegen.domain_definition.application.use_cases.set_value import SetValueCommand

app = typer.Typer(name="set", help="Set a value in blueprint by path")


def _parse_value(value_str: str) -> any:
    """Parse value string - tries JSON first, falls back to string."""
    if not value_str:
        return value_str
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        return value_str


def _parse_key_values(args: List[str]) -> dict:
    """Parse key=value pairs into a dict."""
    result = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            result[key] = _parse_value(value)
    return result


@app.command()
def set_cmd(
    path: str = typer.Argument(
        ...,
        help="Path to set (e.g., 'project.version', 'contexts.sales.aggregates')",
    ),
    value: Optional[str] = typer.Argument(
        None,
        help="JSON value to set (optional if using key=value pairs)",
    ),
    append: bool = typer.Option(
        False,
        "--append",
        "-a",
        help="Append to list instead of replace",
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
    key_values: Optional[List[str]] = typer.Option(
        None,
        "--kv",
        help="Key-value pairs for object creation (e.g., --kv name=Order --kv description=test)",
    ),
):
    """
    Set: Set or update a value in blueprint by path (Upsert).
    
    Use dot notation to navigate. Supports:
    - Simple values: codegen set "project.version" '"2.0.0"'
    - JSON objects: codegen set "contexts" '{"name": "Sales"}' --append
    - Key-value pairs: codegen set "contexts" --append --kv name=Sales --kv description=test
    
    Examples:
        $ codegen set "project.version" '"2.0.0"'
        $ codegen set "contexts.DomainDefinition.description" '"Updated desc"'
        $ codegen set "contexts" '{"name": "Sales", "description": "Sales context"}' --append
        $ codegen set "contexts" --append --kv name=Sales --kv description="Sales context"
    """
    # Determine the value to set
    if key_values:
        parsed_value = _parse_key_values(key_values)
    elif value is not None:
        parsed_value = _parse_value(value)
    else:
        typer.echo("Error: Must provide either a value or --kv key=value pairs", err=True)
        raise typer.Exit(1)
    
    with get_container(config_file=config_file) as container:
        use_case = container.set_value_use_case()
        try:
            use_case.execute(SetValueCommand(
                path=path,
                value=parsed_value,
                append=append,
            ))
            typer.echo(f"Successfully set value at '{path}'")
        except KeyError as e:
            typer.echo(f"Error: Path not found - {e}", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
