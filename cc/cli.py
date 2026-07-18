import subprocess
from typing import Optional

import typer
from loguru import logger

from cc.cascade import run_cascade_merge

app = typer.Typer(help="Custom Cookiecutter CLI for managing hierarchical templates.")


@app.command()
def cascade():
    """
    Cascade merge changes from the current branch into its direct children.
    """
    run_cascade_merge()


@app.command()
def init(
    pyv: Optional[str] = typer.Option(
        "py3.12", "--pyv", help="Python version branch (e.g., 3.12)"
    ),
    cli: bool = typer.Option(False, "--cli", help="Use the script package template"),
    scratch: bool = typer.Option(False, "--scratch", help="Use the scratch template"),
    repo_url: str = typer.Option(
        ...,
        "--repo",
        envvar="FACTORY_URL",
        help="The template repository URL",
    ),
    output_dir: str = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Directory to output the generated project into",
    ),
):
    """
    Initialize a new cookiecutter project from a specific branch hierarchy.
    """
    branch_parts = []

    if pyv:
        branch_parts.append(pyv)

    if cli:
        branch_parts.append("cli")
    elif scratch:
        branch_parts.append("scratch")

    if not branch_parts:
        branch_parts = ["main"]

    branch_name = "--".join(branch_parts)
    logger.info(f"Initializing cookiecutter from branch: {branch_name}")

    try:
        # Run cookiecutter directly wrapping their command
        subprocess.run(
            [
                "cookiecutter",
                repo_url,
                "--checkout",
                branch_name,
                "--output-dir",
                output_dir,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running cookiecutter: {e}")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
