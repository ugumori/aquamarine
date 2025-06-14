"""Console script for aquamarine."""
import aquamarine

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for aquamarine."""
    console.print("Replace this message by putting your code into "
               "aquamarine.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    


if __name__ == "__main__":
    app()
