"""
AddMcpTool command - Add a new MCP tool to a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.add_mcp_tool import (
    AddMcpTool,
    AddMcpToolCommand,
    AddMcpToolResult,
)


@inject
def _add_mcp_tool(
    cmd: AddMcpToolCommand,
    use_case: AddMcpTool = Provide["domain_definition_container.add_mcp_tool"],
) -> AddMcpToolResult:
    return use_case.execute(cmd)


def add_mcp_tool(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="MCP tool name")],
    use_case: Annotated[str, typer.Argument(help="Use case to execute")],
    description: Annotated[str, typer.Argument(help="Tool description")],
) -> None:
    """
    Add a new MCP tool to a bounded context.

    Examples:
        $ codegen interface add-mcp-tool Sales get-orders GetOrders "Get orders via MCP"
        $ codegen interface add-mcp-tool Billing process-payment ProcessPayment "Process payment via MCP"
    """
    cmd = AddMcpToolCommand(
        context_name=context_name,
        name=name,
        use_case=use_case,
        description=description,
    )
    result = _add_mcp_tool(cmd)
    if result.success:
        typer.echo(f"Successfully added MCP tool '{name}' to context '{context_name}'")
    else:
        typer.echo(f"Failed to add MCP tool '{name}' to context '{context_name}'", err=True)
        raise typer.Exit(1)
