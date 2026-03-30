"""
GetDomainService command - Get a domain service from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_domain_service import (
    GetDomainService,
    GetDomainServiceQuery,
    GetDomainServiceResult,
)


@inject
def _get_domain_service(
    query: GetDomainServiceQuery,
    use_case: GetDomainService = Provide[
        "domain_definition_container.get_domain_service"
    ],
) -> GetDomainServiceResult:
    return use_case.execute(query)


def get_domain_service(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain service name")],
) -> None:
    """
    Get a domain service from a bounded context.
    """
    query = GetDomainServiceQuery(
        context_name=context_name,
        name=name,
    )
    result = _get_domain_service(query)
    typer.echo(result.service.model_dump_json(indent=2))
