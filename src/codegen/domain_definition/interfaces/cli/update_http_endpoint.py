"""
UpdateHttpEndpoint command - Update an existing HTTP endpoint in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_http_endpoint import (
    UpdateHttpEndpoint,
    UpdateHttpEndpointCommand,
    UpdateHttpEndpointResult,
)


@inject
def _update_http_endpoint(
    cmd: UpdateHttpEndpointCommand,
    use_case: UpdateHttpEndpoint = Provide[
        "domain_definition_container.update_http_endpoint"
    ],
) -> UpdateHttpEndpointResult:
    return use_case.execute(cmd)


def update_http_endpoint(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    path: Annotated[str, typer.Argument(help="HTTP endpoint path")],
    method: Annotated[str | None, typer.Option("--method", "-m")] = None,
    use_case: Annotated[str | None, typer.Option("--use-case", "-uc")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing HTTP endpoint in a bounded context.

    Examples:
        $ codegen interface update-http-endpoint Sales /orders --method GET --description "Updated endpoint"
        $ codegen interface update-http-endpoint Billing /invoices --use-case ListInvoices
    """
    cmd = UpdateHttpEndpointCommand(
        context_name=context_name,
        path=path,
        method=method,
        use_case=use_case,
        description=description,
    )
    result = _update_http_endpoint(cmd)
    if result.success:
        typer.echo(f"Successfully updated HTTP endpoint '{path}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update HTTP endpoint '{path}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
