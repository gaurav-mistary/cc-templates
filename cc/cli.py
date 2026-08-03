import os
import subprocess
from typing import Optional

import typer
from dotenv import load_dotenv
from loguru import logger

from cc.cascade import run_cascade_merge

app = typer.Typer(help="Custom Cookiecutter CLI for managing hierarchical templates.")

load_dotenv()


def push_git(project_dir: str, push_url: str):
    logger.info(f"Initializing Git repository in {project_dir}...")
    try:
        subprocess.run(
            ["git", "init"], cwd=project_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "branch", "-M", "main"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "add", "."], cwd=project_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "chore(auto): initial commit from cc template"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "remote", "add", "origin", push_url],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )

        logger.info(f"Pushing to {push_url}...")
        subprocess.run(
            ["git", "push", "-u", "origin", "main"], cwd=project_dir, check=True
        )
        logger.success(f"Successfully pushed to {push_url}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {e}")
        if e.stderr:
            logger.error(e.stderr.decode("utf-8", errors="ignore"))


@app.command()
def cascade():
    """
    Cascade merge changes from the current branch into its direct children.
    """
    run_cascade_merge()


@app.command()
def init(
    template: str = typer.Argument(
        "main", help="The template name (e.g., cli, traefik, py3.12--cli)"
    ),
    pyv: Optional[str] = typer.Option(
        None, "--pyv", help="Python version branch prefix (e.g., 3.12)"
    ),
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
    push_url: Optional[str] = typer.Option(
        None,
        "--push-url",
        help="Optional Git remote URL to initialize and push the generated project to",
    ),
):
    """
    Initialize a new cookiecutter project from a specific branch hierarchy.
    """
    if pyv:
        # If the user provides a pyv and a template (not main), combine them.
        # If template is main, just use py3.12 (as the base)
        if template == "main":
            branch_name = f"py{pyv}"
        else:
            branch_name = f"py{pyv}--{template}"
    else:
        branch_name = template

    logger.info(f"Initializing cookiecutter from branch: {branch_name}")

    try:
        before_dirs = (
            set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
        )

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

        if push_url:
            after_dirs = (
                set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
            )
            new_dirs = list(after_dirs - before_dirs)
            if len(new_dirs) == 1:
                project_dir = os.path.join(output_dir, new_dirs[0])
                push_git(project_dir, push_url)
            else:
                logger.error(
                    "Could not determine the exact generated project directory to initialize Git."
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
    push_url: Optional[str] = typer.Option(
        None,
        "--push-url",
        help="Optional Git remote URL to initialize and push the generated project to",
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

            before_dirs = (
                set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
            )

            subprocess.run(
                ["cookiecutter", temp_dir, "--output-dir", output_dir],
                check=True,
            )

            if push_url:
                after_dirs = (
                    set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
                )
                new_dirs = list(after_dirs - before_dirs)
                if len(new_dirs) == 1:
                    project_dir = os.path.join(output_dir, new_dirs[0])
                    push_git(project_dir, push_url)
                else:
                    logger.error(
                        "Could not determine the exact generated project directory to initialize Git."
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
