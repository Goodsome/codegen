"""
GetDomainPort command - Get a domain port from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_domain_port import (
    GetDomainPort,
    GetDomainPortQuery,
    GetDomainPortResult,
)


@inject
def _get_domain_port(
    query: GetDomainPortQuery,
    use_case: GetDomainPort = Provide["domain_definition_container.get_domain_port"],
) -> GetDomainPortResult:
    return use_case.execute(query)


def get_domain_port(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain port name")],
) -> None:
    """
    Get a domain port from a bounded context.
    """
    query = GetDomainPortQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_domain_port(query)
    typer.echo(result.port.model_dump_json(indent=2))
