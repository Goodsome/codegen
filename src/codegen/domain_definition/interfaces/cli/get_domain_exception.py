"""GetDomainException command - Get a domain exception from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_domain_exception import (
    GetDomainException,
    GetDomainExceptionQuery,
    GetDomainExceptionResult,
)


@inject
def _get_domain_exception(
    query: GetDomainExceptionQuery,
    use_case: GetDomainException = Provide[
        "domain_definition_container.get_domain_exception"
    ],
) -> GetDomainExceptionResult:
    return use_case.execute(query)


def get_domain_exception(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain exception name")],
) -> None:
    """
    Get a domain exception from a bounded context.
    """
    query = GetDomainExceptionQuery(context_name=context_name, name=name)
    result = _get_domain_exception(query)
    typer.echo(result.domain_exception.model_dump_json(indent=2))
