"""
UpdateMcpTool command - Update an existing MCP tool in a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.update_mcp_tool import (
    UpdateMcpTool,
    UpdateMcpToolCommand,
    UpdateMcpToolResult,
)


@inject
def _update_mcp_tool(
    cmd: UpdateMcpToolCommand,
    use_case: UpdateMcpTool = Provide["domain_definition_container.update_mcp_tool"],
) -> UpdateMcpToolResult:
    return use_case.execute(cmd)


def update_mcp_tool(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="MCP tool name")],
    use_case: Annotated[str | None, typer.Option("--use-case", "-uc")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
) -> None:
    """
    Update an existing MCP tool in a bounded context.

    Examples:
        $ codegen interface update-mcp-tool Sales get-orders --description "Updated get orders tool"
        $ codegen interface update-mcp-tool Billing process-payment --use-case ProcessNewPayment
    """
    cmd = UpdateMcpToolCommand(
        context_name=context_name,
        name=name,
        use_case=use_case,
        description=description,
    )
    result = _update_mcp_tool(cmd)
    if result.success:
        typer.echo(f"Successfully updated MCP tool '{name}' in context '{context_name}'")
    else:
        typer.echo(f"Failed to update MCP tool '{name}' in context '{context_name}'", err=True)
        raise typer.Exit(1)
