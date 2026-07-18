import json
import os
from datetime import datetime, timezone

import typer
from git import GitCommandError, Repo
from loguru import logger


def get_repo() -> Repo:
    repo_path = os.getcwd()
    try:
        repo = Repo(repo_path, search_parent_directories=True)
        return repo
    except Exception as e:
        logger.error(f"Not a valid git repository. {e}")
        raise typer.Exit(1)


def get_direct_children(repo: Repo, branch_name: str) -> list[str]:
    """Find direct child branches of a given branch name."""
    children = []

    base_depth = branch_name.count("--")
    target_depth = base_depth + 1

    for head in repo.heads:
        if head.name.startswith(f"{branch_name}--"):
            if head.name.count("--") == target_depth:
                children.append(head.name)

    return children


def cascade_merge_recursive(
    repo: Repo, current_branch: str, conflicts_list: list[str], success_list: list[str]
) -> None:
    """Recursively merge current_branch into its children."""
    children = get_direct_children(repo, current_branch)

    if not children:
        logger.debug(f"No direct children found for '{current_branch}'.")
        return

    logger.info(
        f"Found {len(children)} direct children for '{current_branch}': {', '.join(children)}"
    )

    for child in children:
        logger.info(f"Attempting to merge '{current_branch}' into '{child}'")
        try:
            repo.git.checkout(child)
            repo.git.merge(
                current_branch, m=f"Auto-merge '{current_branch}' into '{child}'"
            )
            logger.success(f"Successfully merged '{current_branch}' into '{child}'.")

            logger.info(f"Pushing updated branch '{child}' to remote...")
            repo.git.push("origin", child)

            success_list.append(child)

            # Since merge was successful, we now cascade from child to its children
            logger.info(f"Cascading down from '{child}'...")
            cascade_merge_recursive(repo, child, conflicts_list, success_list)

        except GitCommandError as e:
            logger.error(
                f"MERGE CONFLICT detected for '{child}' when merging '{current_branch}'!"
            )
            repo.git.merge("--abort")
            logger.warning(
                f"Aborted merge for '{child}'. Skipping this branch and its descendants until resolved."
            )
            conflicts_list.append(child)
            # We do NOT recurse into the child because its state is incomplete


def run_cascade_merge():
    repo = get_repo()
    if repo.is_dirty():
        logger.error(
            "Your working directory is not clean. Please commit or stash changes before cascading."
        )
        raise typer.Exit(1)

    original_branch = repo.active_branch.name
    logger.info(f"Starting cascade merge from base branch: '{original_branch}'")

    conflicts_list = []
    success_list = []

    try:
        cascade_merge_recursive(repo, original_branch, conflicts_list, success_list)
    finally:
        logger.info(f"Returning to original branch '{original_branch}'")
        repo.git.checkout(original_branch)

    # Sort lists as requested
    success_list.sort()
    conflicts_list.sort()

    # Generate JSON report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "base_branch": original_branch,
        "successful_merges": success_list,
        "failed_merges": conflicts_list,
    }

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_filename = f"cascade_log_{timestamp_str}.json"
    with open(report_filename, "w") as f:
        json.dump(report, f, indent=4)

    logger.info(f"Report saved to {report_filename}")

    if conflicts_list:
        logger.warning(
            "Cascade merge completed with conflicts in the following branches:"
        )
        for conflict in conflicts_list:
            logger.warning(f" - {conflict}")
        logger.info(
            "Please resolve the conflicts manually. Once resolved, run the cascade command from those branches to continue propagating changes downwards."
        )
    else:
        logger.success(
            "Cascade merge completed successfully across all child branches!"
        )
