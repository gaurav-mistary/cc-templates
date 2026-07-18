import subprocess
from typing import Optional

import typer
from dotenv import load_dotenv
from loguru import logger

from cc.cascade import run_cascade_merge
from cc.enums import TemplateType
from cc.map import MAP

app = typer.Typer(help="Custom Cookiecutter CLI for managing hierarchical templates.")

load_dotenv()


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

    branch_name = "/".join(branch_parts)
    logger.info(f"Initializing cookiecutter from branch: {branch_name}")

    try:
        # Run cookiecutter directly wrapping their command
        subprocess.run(
            ["cookiecutter", repo_url, "--checkout", branch_name], check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running cookiecutter: {e}")
        raise typer.Exit(1)


@app.command()
def create(
    template: TemplateType = typer.Option(
        ..., "--template", help="The template type to initialize"
    ),
    path: str = typer.Option(
        ..., "--path", help="The output directory path for the generated project"
    ),
    pyv: str = typer.Option("3.12", "--pyv", help="Python version branch (e.g., 3.12)"),
    repo_url: str = typer.Option(
        ...,
        "--repo-url",
        envvar="FACTORY_URL",
        help="The template repository URL",
    ),
):
    """
    Initialize a new cookiecutter project from a specific enum template branch.
    """
    if (branch_path := MAP.get(template)) is None:
        raise typer.BadParameter(f"Invalid template type: {template}")

    branch_name = f"py{pyv}{branch_path}"

    logger.info(f"Initializing cookiecutter from branch: {branch_name} into {path}")

    try:
        subprocess.run(
            ["cookiecutter", repo_url, "--checkout", branch_name, "-o", path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running cookiecutter: {e}")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
