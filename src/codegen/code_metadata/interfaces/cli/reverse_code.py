import typer
from typing import Annotated
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from codegen.code_metadata.application.commands.reverse_code import ReverseCode
from codegen.code_metadata.application.dtos.reverse_code_command import ReverseCodeCommand
from codegen.code_metadata.application.dtos.reverse_code_result import ReverseCodeResult

console = Console()


@inject
def _reverse_code(
    cmd: ReverseCodeCommand,
    use_case: ReverseCode= Provide["code_metadata_container.reverse_code"],
) -> ReverseCodeResult:
    return use_case.execute(cmd)


def reverse_code(
    context: Annotated[str, typer.Argument()],
    component_type: Annotated[str, typer.Argument()],
) -> None:
    """Reverse code."""
    cmd = ReverseCodeCommand(context=context, component_type=component_type)
    _reverse_code(cmd)
