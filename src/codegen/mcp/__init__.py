"""
Codegen MCP Server Module.

Exposes codegen CLI commands as MCP tools for LLM integration.
"""

from codegen.mcp.server import mcp

__all__ = ["mcp"]


def run():
    """Entry point for MCP server."""
    mcp.run()
