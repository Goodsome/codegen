"""AddDomainException command - Add a new domain exception to a bounded context."""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_domain_exception import (
    AddDomainException,
    AddDomainExceptionCommand,
    AddDomainExceptionResult,
)


@inject
def _add_domain_exception(
    cmd: AddDomainExceptionCommand,
    use_case: AddDomainException = Provide[
        "domain_definition_container.add_domain_exception"
    ],
) -> AddDomainExceptionResult:
    return use_case.execute(cmd)


def add_domain_exception(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="Domain exception name (PascalCase)")],
    description: Annotated[str, typer.Argument(help="Domain exception description")],
) -> None:
    """
    Add a new domain exception to a bounded context.
    """
    cmd = AddDomainExceptionCommand(
        context_name=context_name,
        name=name,
        description=description,
    )
    result = _add_domain_exception(cmd)
    if result.success:
        typer.echo(f"Successfully added domain exception '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add domain exception '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
