"""
GetHttpEndpoint command - Get an HTTP endpoint from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_http_endpoint import (
    GetHttpEndpoint,
    GetHttpEndpointQuery,
    GetHttpEndpointResult,
)


@inject
def _get_http_endpoint(
    cmd: GetHttpEndpointQuery,
    use_case: GetHttpEndpoint = Provide[
        "domain_definition_container.get_http_endpoint"
    ],
) -> GetHttpEndpointResult:
    return use_case.execute(cmd)


def get_http_endpoint(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    path: Annotated[str, typer.Argument(help="HTTP endpoint path")],
) -> None:
    """
    Get an HTTP endpoint from a bounded context.

    Examples:
        $ codegen interface get-http-endpoint Sales /orders
        $ codegen interface get-http-endpoint Billing /invoices
    """
    cmd = GetHttpEndpointQuery(context_name=context_name, path=path)
    result = _get_http_endpoint(cmd)
    typer.echo(result.http_endpoint.model_dump_json(indent=2))
