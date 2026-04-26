"""RemoveDomainException command - Remove a domain exception from a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_domain_exception import (
    RemoveDomainException,
    RemoveDomainExceptionCommand,
    RemoveDomainExceptionResult,
)


@inject
def _remove_domain_exception(
    cmd: RemoveDomainExceptionCommand,
    use_case: RemoveDomainException = Provide[
        "domain_definition_container.remove_domain_exception"
    ],
) -> RemoveDomainExceptionResult:
    return use_case.execute(cmd)


def remove_domain_exception(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain exception name")],
) -> None:
    """
    Remove a domain exception from a bounded context.
    """
    cmd = RemoveDomainExceptionCommand(
        context_name=context_name,
        name=name,
    )
    result = _remove_domain_exception(cmd)
    if result.success:
        typer.echo(f"Successfully removed domain exception '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove domain exception '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
