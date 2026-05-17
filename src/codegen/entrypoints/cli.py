import typer

from codegen.bootstrap.logging import setup_cli_logging
from codegen.bootstrap.setup import create_container
from codegen.orchestration.interfaces.cli.build import scaffold
from codegen.orchestration.interfaces.cli.reverse import reverse
from codegen.python_gen.interfaces.cli.schema import schema
from codegen.domain_definition.interfaces.cli.tree import tree as tree_cmd
from codegen.domain_definition.interfaces.cli.init import init
from codegen.code_metadata.interfaces.cli.generate_code import generate_code
from codegen.code_metadata.interfaces.cli.get_dev_progress import get_dev_progress
from codegen.code_metadata.interfaces.cli.list_components import list_components
from codegen.code_metadata.interfaces.cli.reverse_code import reverse_code

app = typer.Typer(
    name="codegen",
    help="""Codegen CLI - DDD Project Scaffolding Tool.

**Commands**:
  init             Initialize a new codegen.yaml blueprint
  scaffold         Generate Python code skeleton from codegen.yaml
  reverse          Reverse-engineer Python code into codegen.yaml
  schema           Output JSON schema for the blueprint
  tree             Display blueprint structure as a visual tree
  get-dev-progress Show development progress with AST similarity metrics
    """,
    add_completion=False,
    rich_markup_mode="markdown",
)

# Root Commands
app.command()(scaffold)
app.command()(reverse)
app.command()(schema)
app.command()(init)
app.command()(generate_code)
app.command()(get_dev_progress)
app.command()(reverse_code)
app.command()(list_components)
app.command(name="tree")(tree_cmd)


def main():
    """Bootstrap the DI container and run the CLI app."""
    setup_cli_logging()
    container = create_container()
    container.wire(
        packages=[
            "codegen.orchestration.interfaces.cli",
            "codegen.domain_definition.interfaces.cli",
            "codegen.python_gen.interfaces.cli",
            "codegen.code_metadata.interfaces.cli",
        ]
    )
    app()


if __name__ == "__main__":
    main()
