"""
Get command - Query a value from blueprint by path.

New path-based command for inspecting blueprint values.
"""

import json
from pathlib import Path

import typer
from pydantic import BaseModel
from codegen.cli.utils import get_container
from codegen.domain_definition.application.use_cases.path_operations import (
    GetValueCommand,
)

app = typer.Typer(name="get", help="Get a value from blueprint by path")


def _serialize_value(value, format: str) -> str:
    """Serialize value to string for output."""
    if isinstance(value, BaseModel):
        if format == "yaml":
            import yaml
            return yaml.dump(value.model_dump(), allow_unicode=True, default_flow_style=False)
        return value.model_dump_json(indent=2)
    
    if isinstance(value, (list, dict)):
        if format == "yaml":
            import yaml
            # Convert Pydantic models in list/dict
            def to_dict(obj):
                if isinstance(obj, BaseModel):
                    return obj.model_dump()
                if isinstance(obj, list):
                    return [to_dict(item) for item in obj]
                if isinstance(obj, dict):
                    return {k: to_dict(v) for k, v in obj.items()}
                return obj
            return yaml.dump(to_dict(value), allow_unicode=True, default_flow_style=False)
        return json.dumps(
            value if not any(isinstance(v, BaseModel) for v in (value if isinstance(value, list) else [value]))
            else [v.model_dump() if isinstance(v, BaseModel) else v for v in value] if isinstance(value, list)
            else value,
            indent=2,
            ensure_ascii=False,
            default=lambda o: o.model_dump() if isinstance(o, BaseModel) else str(o)
        )
    
    return str(value)


@app.command()
def get_cmd(
    path: str = typer.Argument(
        ...,
        help="Path to query (e.g., 'project.name', 'contexts.sales.aggregates')",
    ),
    config_file: Path = typer.Option(
        Path("codegen.yaml"),
        "--config",
        "-c",
        help="Path to the codegen.yaml blueprint file",
    ),
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json or yaml",
    ),
):
    """
    Get: Query a value from blueprint by path.
    
    Use dot notation to navigate the blueprint structure.
    Supports index access with [n] syntax.
    
    Examples:
        $ codegen get "name"
        $ codegen get "contexts"
        $ codegen get "contexts.DomainDefinition"
        $ codegen get "contexts[0].domain.aggregates"
    """
    with get_container(config_file=config_file) as container:
        use_case = container.get_value_use_case()
        try:
            result = use_case.execute(GetValueCommand(path=path))
            typer.echo(_serialize_value(result, output_format))
        except KeyError as e:
            typer.echo(f"Error: Path not found - {e}", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
