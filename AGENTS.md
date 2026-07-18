# Custom Cookiecutter (CC) Templates Context

## Project Overview
This repository contains a highly opinionated, hierarchical Cookiecutter templating system. The core concept is **branch-based template inheritance**. 
Instead of keeping all templates in subdirectories on a single main branch, this project uses a Git branching hierarchy (e.g., `parent/child1/child2`). A base change in a parent branch (like `python3.12`) automatically cascades down to all child branches (like `python3.12/script-package`), integrating changes while respecting custom modifications at the lower levels via intelligent Git merging.

## Core Tooling: `cc-cli`
The automation is handled by a custom Python CLI tool located in the `cc/` directory. It uses `typer` for the interface, `loguru` for verbose logging, and `GitPython` for git operations.

### Key Commands:
1. **`cc-cli init`**: Wraps the standard `cookiecutter` CLI. It parses arguments (e.g., `--pyv 3.12 --script`) to dynamically construct the target branch name (e.g., `python3.12/script-package`) and initializes a project from that branch.
2. **`cc-cli cascade`**: Executes the cascading merge logic.
   - Starts at the current branch.
   - Discovers all *direct* children by parsing remote branch names for a `/` hierarchy.
   - Merges the parent into the child and pushes the child to `origin`.
   - Recursively cascades down the tree if successful.
   - Generates a JSON report (`cascade_log_YYYYMMDD_HHMMSS.json`) detailing successful and failed merges.
   - **Conflict Handling**: If a merge conflict occurs, the script aborts the merge, logs the conflict, and intentionally **halts recursion for that specific descendant path**, but continues processing other sibling branches safely.

## Automation & CI/CD
- **GitHub Action (`cascade.yml`)**: On every `push` (or PR merge) to any branch (except `main`), the Action checks out the repository (`fetch-depth: 0`) and runs `uv run cc-cli cascade`. It relies on the default `GITHUB_TOKEN` to push the merged branches back. It uploads the dynamically named JSON merge report as a GitHub artifact.
- **Pre-commit**: Installed locally. `black` and `isort` enforce perfectly formatted Python code on every commit.

## Task Runner (`just`)
The repository uses `just` as an alias router.
- The root `justfile` registers a module: `mod cc`.
- `cc.just` contains aliases like `just cc cascade` or `just cc init-script` which expand to specific `uv run cc-cli` argument combinations.

## Typical Conflict Workflow
If an automated cascade merge encounters a conflict (e.g., on `parent/level1`), the workflow is:
1. The developer checks out `parent/level1`.
2. The developer manually resolves the merge conflict with `parent`.
3. The developer commits the fix and opens/merges a PR.
4. The GitHub Action automatically runs against the newly updated `parent/level1` branch, and seamlessly resumes cascading the changes down to `parent/level1/level2`.
