"""
RemoveHttpEndpoint command - Remove an HTTP endpoint from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_http_endpoint import (
    RemoveHttpEndpoint,
    RemoveHttpEndpointCommand,
    RemoveHttpEndpointResult,
)


@inject
def _remove_http_endpoint(
    cmd: RemoveHttpEndpointCommand,
    use_case: RemoveHttpEndpoint = Provide[
        "domain_definition_container.remove_http_endpoint"
    ],
) -> RemoveHttpEndpointResult:
    return use_case.execute(cmd)


def remove_http_endpoint(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    path: Annotated[str, typer.Argument(help="HTTP endpoint path")],
) -> None:
    """
    Remove an HTTP endpoint from a bounded context.

    Examples:
        $ codegen interface remove-http-endpoint Sales /orders
        $ codegen interface remove-http-endpoint Billing /invoices
    """
    cmd = RemoveHttpEndpointCommand(context_name=context_name, path=path)
    result = _remove_http_endpoint(cmd)
    if result.success:
        typer.echo(f"Successfully removed HTTP endpoint '{path}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove HTTP endpoint '{path}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
