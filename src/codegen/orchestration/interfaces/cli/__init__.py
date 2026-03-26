import typer
from codegen.orchestration.interfaces.cli.build import build

app = typer.Typer(help="Orchestration CLI")
app.command("build")(build)
