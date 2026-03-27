"""
Set command - Set or update a value in blueprint by path.
"""
import json
from typing import Annotated, Optional, List, Any

import typer
from dependency_injector.wiring import Provide, inject
from codegen.domain_definition.application.use_cases.set_value import (
    SetValue,
    SetValueCommand,
)


def _parse_value(value_str: str) -> Any:
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


@inject
def _set_value(
    cmd: SetValueCommand,
    use_case: SetValue = Provide["domain_definition_container.set_value"],
) -> None:
    return use_case.execute(cmd)


def set(
    path: Annotated[str, typer.Argument(
        help="Path to set (e.g., 'project.version', 'contexts.sales.aggregates')",
    )],
    value: Annotated[Optional[str], typer.Argument(
        help="JSON value to set (optional if using key=value pairs)",
    )] = None,
    append: Annotated[bool, typer.Option("--append", "-a")] = False,
    key_values: Annotated[Optional[List[str]], typer.Option(
        "--kv",
        help="Key-value pairs for object creation (e.g., --kv name=Order --kv description=test)",
    )] = None,
) -> None:
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
    if key_values:
        parsed_value = _parse_key_values(key_values)
    elif value is not None:
        parsed_value = _parse_value(value)
    else:
        typer.echo("Error: Must provide either a value or --kv key=value pairs", err=True)
        raise typer.Exit(1)

    cmd = SetValueCommand(
        path=path,
        value=parsed_value,
        append=append,
    )
    _set_value(cmd)
    typer.echo(f"Successfully set value at '{path}'")
