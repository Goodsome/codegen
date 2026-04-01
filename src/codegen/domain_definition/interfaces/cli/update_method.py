import typer
from typing import Annotated, Union, Any
from dependency_injector.wiring import Provide, inject
from codegen.domain_definition.application.use_cases.update_method import (
    UpdateMethod,
    UpdateMethodCommand,
    UpdateMethodResult,
)
from codegen.domain_definition.domain.enums import ElementType, MethodKind
from codegen.shared.domain.enums import ContainerType


@inject
def _update_method(
    cmd: UpdateMethodCommand,
    use_case: UpdateMethod = Provide["domain_definition_container.update_method"],
) -> UpdateMethodResult:
    return use_case.execute(cmd)


def update_method(
    context_name: Annotated[str, typer.Argument()],
    element_type: Annotated[ElementType, typer.Argument()],
    method_kind: Annotated[MethodKind, typer.Argument()],
    element_name: Annotated[str, typer.Argument()],
    name: Annotated[str, typer.Argument()],
    description: Annotated[str, typer.Argument()],
    output_type: Annotated[str, typer.Argument()],
    inputs: Annotated[str | None, typer.Option("--inputs", "-i")] = None,
    output_container: Annotated[
        ContainerType, typer.Option("--output-container", "-oc")
    ] = ContainerType.NONE,
    output_optional: Annotated[bool, typer.Option("--output-optional", "-oo")] = False,
    output_custom_type_string: Annotated[
        str | None, typer.Option("--output-custom-type-string", "-octs")
    ] = None,
) -> None:
    """Update a method of an element.

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
        output_container=output_container,
        output_custom_type_string=output_custom_type_string,
    )
    result = _update_method(cmd)
    if result.success:
        typer.echo(f"Successfully updated {method_kind.value} '{name}'")
    else:
        typer.echo(f"Failed to update {method_kind.value} '{name}'", err=True)
        raise typer.Exit(1)
