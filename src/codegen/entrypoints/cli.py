import typer

from codegen.bootstrap.logging import setup_cli_logging
from codegen.bootstrap.setup import create_container
from codegen.orchestration.interfaces.cli.build import scaffold
from codegen.orchestration.interfaces.cli.reverse import reverse
from codegen.python_gen.interfaces.cli.schema import schema
from codegen.code_metadata.interfaces.cli.get_directory_tree import get_directory_tree as tree_cmd
from codegen.domain_definition.interfaces.cli.init import init
from codegen.code_metadata.interfaces.cli.delete_component import delete_component
from codegen.code_metadata.interfaces.cli.ingest_project import ingest_project
from codegen.code_metadata.interfaces.cli.generate_code import generate_code
from codegen.code_metadata.interfaces.cli.get_dev_progress import get_dev_progress
from codegen.code_metadata.interfaces.cli.list_components import list_components
from codegen.code_metadata.interfaces.cli.reverse_code import reverse_code
from codegen.code_metadata.interfaces.cli.get_component import get_component
from codegen.code_metadata.interfaces.cli.get_module import get_module
from codegen.code_metadata.interfaces.cli.list_modules import list_modules
from codegen.code_dom.interfaces.cli.get_file_document import get_file_document



app = typer.Typer(
    name="codegen",
    help="""Codegen CLI - DDD Project Scaffolding Tool.

**Commands**:
  init             Initialize a new codegen.yaml blueprint
  scaffold         Generate Python code skeleton from codegen.yaml
  reverse          Reverse-engineer Python code into codegen.yaml
  schema           Output JSON schema for the blueprint
  get-module       Get module by path
  tree             Display code-node directory tree by FQN prefix
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
app.command()(get_component)
app.command()(get_module)
app.command()(list_modules)

app.command()(delete_component)
app.command()(ingest_project)
app.command()(get_file_document)

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
            "codegen.code_dom.interfaces.cli",
        ]
    )
    app()


if __name__ == "__main__":
    main()
