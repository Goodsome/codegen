import typer
from codegen.domain_definition.interfaces.cli.get import get

app = typer.Typer(help="DomainDefinition CLI")
app.command("get")(get)
