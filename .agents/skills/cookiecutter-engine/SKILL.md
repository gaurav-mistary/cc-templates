---
name: cookiecutter-engine
description: Architecture and commands for the Git-Branch based Cookiecutter Engine (`cc`). Trigger when asked to modify the CLI, add base branches, or perform cascade merges.
---

# Cookiecutter Engine (cc)

You are operating inside `cc`, the core engine repository for a branch-based cookiecutter system. 

## The Golden Rules
1. **Never build hybrid templates in `cc`**. The `cc` repo is strictly for the CLI engine (`main` branch) and root-level Base Templates (e.g., `traefik`, `dockhand`, `py3.12` directly off `main`).
2. Hybrid templates (like `traefik--dockhand`) belong in the user's fork (`cc-templates`).
3. If you make a change to a base template (e.g. `traefik`) in `cc`, you MUST run `just cc cascade` so that the change propagates to any child branches.

## Common Operations
- Format code: `uv run pre-commit run --all-files`
- Run cascade: `just cc cascade`
- The CLI tool is located in `cc/cli.py`.
