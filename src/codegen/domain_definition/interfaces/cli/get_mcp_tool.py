"""
GetMcpTool command - Get an MCP tool from a bounded context.
"""
from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject

from codegen.domain_definition.application.use_cases.get_mcp_tool import (
    GetMcpTool,
    GetMcpToolQuery,
    GetMcpToolResult,
)


@inject
def _get_mcp_tool(
    cmd: GetMcpToolQuery,
    use_case: GetMcpTool = Provide["domain_definition_container.get_mcp_tool"],
) -> GetMcpToolResult:
    return use_case.execute(cmd)


def get_mcp_tool(
    context_name: Annotated[str, typer.Argument(help="Bounded context name")],
    name: Annotated[str, typer.Argument(help="MCP tool name")],
) -> None:
    """
    Get an MCP tool from a bounded context.

    Examples:
        $ codegen interface get-mcp-tool Sales get-orders
        $ codegen interface get-mcp-tool Billing process-payment
    """
    cmd = GetMcpToolQuery(context_name=context_name, name=name)
    result = _get_mcp_tool(cmd)
    typer.echo(result.mcp_tool.model_dump_json(indent=2))
