import typer

from .create_token import create_token as create_token_command
from .download import download as download_command

app = typer.Typer(
    name="next-cvat",
    help="CLI tool for downloading and handling CVAT annotations",
)


app.command(create_token_command)
app.command(download_command)
