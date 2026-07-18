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
        None, "--pyv", help="Python version branch (e.g., 3.12)"
    ),
    script: bool = typer.Option(
        False, "--script", help="Use the script package template"
    ),
    scratch: bool = typer.Option(False, "--scratch", help="Use the scratch template"),
    django: bool = typer.Option(False, "--django", help="Use the django template"),
    webapp: bool = typer.Option(False, "--webapp", help="Use the webapp template"),
    repo_url: str = typer.Option(
        "https://github.com/yourusername/your-repo",
        "--repo",
        help="The template repository URL",
    ),
):
    """
    Initialize a new cookiecutter project from a specific branch hierarchy.
    """
    branch_parts = []

    if pyv:
        branch_parts.append(f"python{pyv}")

    if script:
        branch_parts.append("script-package")
    elif scratch:
        branch_parts.append("scratch")
    elif django:
        branch_parts.append("django")
    elif webapp:
        branch_parts.append("webapp")

    if not branch_parts:
        branch_parts = ["main"]

    branch_name = "--".join(branch_parts)
    logger.info(f"Initializing cookiecutter from branch: {branch_name}")

    try:
        # Run cookiecutter directly wrapping their command
        subprocess.run(
            ["cookiecutter", repo_url, "--checkout", branch_name], check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running cookiecutter: {e}")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
