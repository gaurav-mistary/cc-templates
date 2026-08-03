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


@app.command()
def mix(
    base: str = typer.Argument(..., help="The base branch (e.g., py3.12)"),
    mixin: str = typer.Argument(..., help="The branch to mix in (e.g., traefik)"),
    output_dir: str = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Directory to output the generated project into",
    ),
    repo_url: str = typer.Option(
        ...,
        "--repo",
        envvar="FACTORY_URL",
        help="The template repository URL",
    ),
):
    """
    Mix two template branches on the fly in a temporary directory and generate a project.
    Aborts cleanly if there is a merge conflict.
    """
    import tempfile

    logger.info(f"Mixing '{mixin}' into '{base}' from {repo_url}")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone repo to temp dir
            subprocess.run(
                ["git", "clone", repo_url, temp_dir],
                check=True,
                capture_output=True,
            )

            # Checkout base
            subprocess.run(
                ["git", "checkout", base],
                cwd=temp_dir,
                check=True,
                capture_output=True,
            )

            # Merge mixin
            merge_proc = subprocess.run(
                ["git", "merge", f"origin/{mixin}", "--no-edit"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            if merge_proc.returncode != 0:
                logger.error(
                    f"Merge conflict detected when mixing '{mixin}' into '{base}'."
                )
                logger.error(
                    "Aborting mix. To resolve this, you can manually create a merged branch:"
                )
                logger.error(f"  1. git checkout -b {base}--{mixin} origin/{base}")
                logger.error(f"  2. git merge origin/{mixin}")
                logger.error(f"  3. Resolve conflicts and commit")
                logger.error(
                    f"  4. Use `cc init` (or standard cookiecutter) on your new branch"
                )
                raise typer.Exit(1)

            logger.info("Merge successful! Running cookiecutter...")

            subprocess.run(
                ["cookiecutter", temp_dir, "--output-dir", output_dir],
                check=True,
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"Error during mixing: {e}")
            if e.stderr:
                try:
                    logger.error(e.stderr.decode("utf-8"))
                except AttributeError:
                    pass
            raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
