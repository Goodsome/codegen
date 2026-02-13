"""
MCP command - Start the Codegen MCP server.

Allows LLMs to interact with codegen via Model Context Protocol.
"""

import typer

app = typer.Typer(name="mcp", help="Start the Codegen MCP server")


@app.command()
def mcp_cmd(
    transport: str = typer.Option(
        "stdio",
        "--transport",
        "-t",
        help="Transport mode: stdio or http",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port for HTTP transport (only used with --transport http)",
    ),
):
    """
    Start the Codegen MCP server.

    The MCP server exposes codegen commands as tools that can be called
    by LLMs via the Model Context Protocol.

    Available tools:
      - build: Compile codegen.yaml into Python code
      - reverse: Reverse-engineer Python code into codegen.yaml
      - tree: Display blueprint structure
      - get: Query a value from blueprint by path
      - set: Set or update a value in blueprint by path
      - rm: Remove a value from blueprint by path

    Examples:
        $ codegen mcp                    # Start with stdio transport
        $ codegen mcp --transport http   # Start with HTTP transport
    """
    from codegen.mcp.server import mcp

    if transport == "http":
        mcp.run(transport="http", port=port)
    else:
        mcp.run()
