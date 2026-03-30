"""
RemoveMcpTool command - Remove an MCP tool from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.remove_mcp_tool import (
    RemoveMcpTool,
    RemoveMcpToolCommand,
    RemoveMcpToolResult,
)


@inject
def _remove_mcp_tool(
    cmd: RemoveMcpToolCommand,
    use_case: RemoveMcpTool = Provide["domain_definition_container.remove_mcp_tool"],
) -> RemoveMcpToolResult:
    return use_case.execute(cmd)


def remove_mcp_tool(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="MCP tool name")],
) -> None:
    """
    Remove an MCP tool from a bounded context.

    Examples:
        $ codegen interface remove-mcp-tool Sales get-orders
        $ codegen interface remove-mcp-tool Billing process-payment
    """
    cmd = RemoveMcpToolCommand(context_name=context_name, name=name)
    result = _remove_mcp_tool(cmd)
    if result.success:
        typer.echo(f"Successfully removed MCP tool '{name}' from context '{context_name}'")
    else:
        typer.echo(f"Failed to remove MCP tool '{name}' from context '{context_name}'", err=True)
        raise typer.Exit(1)
