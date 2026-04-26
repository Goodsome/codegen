"""GetDomain command - Get the domain spec from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_domain import (
    GetDomain,
    GetDomainQuery,
    GetDomainResult,
)


@inject
def _get_domain(
    query: GetDomainQuery,
    use_case: GetDomain = Provide["domain_definition_container.get_domain"],
) -> GetDomainResult:
    return use_case.execute(query)


def get_domain(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
) -> None:
    """
    Get the domain spec from a bounded context.
    """
    query = GetDomainQuery(context_name=context_name)
    result = _get_domain(query)
    typer.echo(result.domain.model_dump_json(indent=2))
