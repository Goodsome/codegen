"""
AddHttpEndpoint command - Add a new HTTP endpoint to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_http_endpoint import (
    AddHttpEndpoint,
    AddHttpEndpointCommand,
    AddHttpEndpointResult,
)


@inject
def _add_http_endpoint(
    cmd: AddHttpEndpointCommand,
    use_case: AddHttpEndpoint = Provide[
        "domain_definition_container.add_http_endpoint"
    ],
) -> AddHttpEndpointResult:
    return use_case.execute(cmd)


def add_http_endpoint(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    path: Annotated[str, typer.Argument(help="HTTP endpoint path (e.g., /orders)")],
    method: Annotated[str, typer.Argument(help="HTTP method (GET, POST, PUT, DELETE, etc.)")],
    use_case: Annotated[str, typer.Argument(help="Use case to execute")],
    description: Annotated[str, typer.Argument(help="Endpoint description")],
) -> None:
    """
    Add a new HTTP endpoint to a bounded context.

    Examples:
        $ codegen interface add-http-endpoint Sales /orders GET ListOrders "List all orders"
        $ codegen interface add-http-endpoint Billing /invoices POST CreateInvoice "Create a new invoice"
    """
    cmd = AddHttpEndpointCommand(
        context_name=context_name,
        path=path,
        method=method,
        use_case=use_case,
        description=description,
    )
    result = _add_http_endpoint(cmd)
    if result.success:
        typer.echo(f"Successfully added HTTP endpoint '{method} {path}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add HTTP endpoint '{method} {path}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
