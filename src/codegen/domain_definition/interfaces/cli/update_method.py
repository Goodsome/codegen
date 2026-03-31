"""
UpdateMethod command - Update a method of an element.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_method import (
    UpdateMethod,
    UpdateMethodCommand,
    UpdateMethodResult,
)
from codegen.domain_definition.domain.enums import ElementType, MethodKind


@inject
def _update_method(
    cmd: UpdateMethodCommand,
    use_case: UpdateMethod = Provide["domain_definition_container.update_method"],
) -> UpdateMethodResult:
    return use_case.execute(cmd)


def update_method(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    element_type: Annotated[ElementType, typer.Argument(help="Element type")],
    method_kind: Annotated[MethodKind, typer.Argument(help="Method kind")],
    element_name: Annotated[str, typer.Argument(help="Element name")],
    name: Annotated[str, typer.Argument(help="Method name to update")],
    output_type: Annotated[str | None, typer.Option("--output-type", "-t")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
    inputs: Annotated[str | None, typer.Option("--inputs", "-i", help="JSON string of inputs list")] = None,
    output_optional: Annotated[bool | None, typer.Option("--output-optional")] = None,
) -> None:
    """
    Update a method of an element.

    Examples:
        $ codegen field update-method sales entity behavior Order calculate_total --output-type float
    """
    import json

    parsed_inputs = None
    if inputs:
        parsed_inputs = json.loads(inputs)

    cmd = UpdateMethodCommand(
        context_name=context_name,
        element_type=element_type,
        method_kind=method_kind,
        element_name=element_name,
        name=name,
        description=description,
        inputs=parsed_inputs,
        output_type=output_type,
        output_optional=output_optional,
    )
    result = _update_method(cmd)
    if result.success:
        typer.echo(f"Successfully updated {method_kind.value} '{name}'")
    else:
        typer.echo(f"Failed to update {method_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
