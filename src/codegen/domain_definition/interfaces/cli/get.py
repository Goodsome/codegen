import json

import typer
from pydantic import BaseModel
from typing import Annotated

from codegen.domain_definition.application.use_cases.get_value import (
    GetValue,
    GetValueCommand,
    GetValueResult,
)
from dependency_injector.wiring import Provide, inject


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


@inject
def _get_value(
    cmd: GetValueCommand,
    use_case: GetValue = Provide["domain_definition_container.get_value"],
) -> GetValueResult:
    return use_case.execute(cmd)


def get(
    path: Annotated[str, typer.Argument(
        ...,
        help="Path to query (e.g., 'project.name', 'contexts.sales.aggregates')",
    )],
    output_format: Annotated[str, typer.Option(
        "--format",
        "-f",
        help="Output format: json or yaml",
    )] = "json",
) -> GetValueResult:
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
    cmd = GetValueCommand(path=path)
    result = _get_value(cmd)
    typer.echo(_serialize_value(result, output_format))
    return result
