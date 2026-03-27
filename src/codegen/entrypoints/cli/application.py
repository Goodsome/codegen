import typer

from codegen.bootstrap import bootstrap
from codegen.orchestration.interfaces.cli.build import build
from codegen.orchestration.interfaces.cli.reverse import reverse
from codegen.python_gen.interfaces.cli.schema import schema
from codegen.domain_definition.interfaces.cli.get import get as get_cmd
from codegen.domain_definition.interfaces.cli.set import set as set_cmd
from codegen.domain_definition.interfaces.cli.rm import rm
from codegen.domain_definition.interfaces.cli.tree import tree as tree_cmd
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


def main():
    """Bootstrap the DI container and run the CLI app."""
    container = bootstrap()
    container.wire(packages=[
        "codegen.orchestration.interfaces.cli",
        "codegen.domain_definition.interfaces.cli",
        "codegen.python_gen.interfaces.cli",
    ])
    app()


if __name__ == "__main__":
    main()
