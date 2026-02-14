import typer
from codegen.cli.utils import version_callback

# New path-based commands
from codegen.cli.commands.build import build
from codegen.cli.commands.reverse import reverse
from codegen.cli.commands.schema import schema
from codegen.cli.commands.get import get_cmd
from codegen.cli.commands.set import set_cmd
from codegen.cli.commands.rm import rm
from codegen.cli.commands.tree import tree_cmd
from codegen.cli.commands.mcp_cmd import mcp_cmd

app = typer.Typer(
    name="codegen",
    help="""Codegen CLI - DDD Project Scaffolding Tool.

**Core Commands (Lifecycle)**:
  build      Compile codegen.yaml into Python code
  reverse    Reverse-engineer Python code into codegen.yaml
  schema     Output JSON schema for the blueprint

**Overview Command**:
  tree       Display blueprint structure as a visual tree

**Edit Commands (Blueprint Manipulation)**:
  get        Get a value by path (e.g., 'contexts.sales')
  set        Set a value by path (Upsert). Supports --append for lists
  rm         Remove a value by path

**Options**:
  -c, --config PATH   Path to codegen.yaml [default: ./codegen.yaml]
  --help              Show this message

**Examples**:
  $ codegen build --overwrite
  $ codegen set "project.version" '"1.2.0"'
  $ codegen get "contexts.DomainDefinition.domain.aggregates"
  $ codegen rm "contexts.Test"

For more information, see: https://github.com/Goodsome/codegen
    """,
    add_completion=False,
    rich_markup_mode="markdown",
)

# ============================================================================
# New Path-Based Commands (Primary)
# ============================================================================

app.command()(build)
app.command()(reverse)
app.command()(schema)
app.command(name="tree")(tree_cmd)
app.command(name="get")(get_cmd)
app.command(name="set")(set_cmd)
app.command()(rm)
app.command(name="mcp")(mcp_cmd)



if __name__ == "__main__":
    app()
