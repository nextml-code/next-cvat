from pathlib import Path
from typing import Optional

import typer

from .create_token import create_token as create_token_command
from .download import download as download_command
from .settings import Settings

app = typer.Typer(
    name="next-cvat",
    help="CLI tool for downloading and handling CVAT annotations",
)


@app.command()
def create_token(
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Prompt for credentials interactively"
    ),
    env_file: Optional[Path] = typer.Option(
        None,
        "--env-file",
        "-f",
        help="Load credentials from a specific .env file",
    ),
):
    """
    Create an authentication token for CVAT.

    Credentials are loaded in the following order:
    1. Interactive prompt (if --interactive flag is set)
    2. Specified env file (if --env-file is provided)
    3. Default environment variables (CVAT_USERNAME, CVAT_PASSWORD)
    4. Interactive prompt (if no credentials were found)
    """
    if interactive:
        username = typer.prompt("Enter your CVAT username")
        password = typer.prompt("Enter your CVAT password", hide_input=True)
    else:
        settings = Settings(env_file=env_file)
        if not settings.username or not settings.password:
            typer.echo(
                "No credentials found in environment, switching to interactive mode"
            )
            username = typer.prompt("Enter your CVAT username")
            password = typer.prompt("Enter your CVAT password", hide_input=True)
        else:
            username = settings.username
            password = settings.password

    create_token_command(username=username, password=password)


@app.command()
def download(
    project_id: str = typer.Option(..., "--project-id", help="CVAT project ID"),
    dataset_path: Path = typer.Option(
        ...,
        "--dataset-path",
        help="Path where the dataset will be saved",
        dir_okay=True,
        file_okay=False,
    ),
):
    """
    Download annotations and images from a CVAT project.
    """
    download_command(project_id=project_id, dataset_path=dataset_path)


def main():
    app()


if __name__ == "__main__":
    main()
