import typer

# New path-based commands
from codegen.entrypoints.cli.commands.build import build
from codegen.entrypoints.cli.commands.reverse import reverse
from codegen.entrypoints.cli.commands.schema import schema
from codegen.entrypoints.cli.commands.get import get_cmd
from codegen.entrypoints.cli.commands.set import set_cmd
from codegen.entrypoints.cli.commands.rm import rm
from codegen.entrypoints.cli.commands.tree import tree_cmd
from codegen.entrypoints.cli.commands.init import init

app = typer.Typer(
    name="codegen",
    help="""Codegen CLI - DDD Project Scaffolding Tool.

**Core Commands (Lifecycle)**:
  init       Initialize a new codegen.yaml blueprint
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
  $ codegen init
  $ codegen build
  $ codegen build --node DomainDefinition
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
app.command()(init)
app.command(name="tree")(tree_cmd)
app.command(name="get")(get_cmd)
app.command(name="set")(set_cmd)
app.command()(rm)


if __name__ == "__main__":
    app()
