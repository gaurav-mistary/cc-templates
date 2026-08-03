---
name: cookiecutter-templates
description: Instructions for managing the user's hybrid Cookiecutter templates. Trigger when asked to create or update template mixes in `cc-templates`.
---

# Cookiecutter Templates (`cc-templates`)

You are operating inside `cc-templates`, a fork of the `cc` engine. This repository is dedicated to building and maintaining hybrid/mixed templates.

## The Golden Rules
1. **Never edit `cc-cli` code here**. The `main` branch code is maintained upstream in the `cc` repository.
2. **Hybrid Branches**: When the user asks for a combination template, create a new branch combining the names of the bases (e.g., `traefik--secure--dockhand`).
3. **Merge Conflicts**: When mixing templates (e.g. `docker-compose.yml`), manually resolve the conflicts to ensure both templates function simultaneously.
4. **The Registry**: If you create a new hybrid template, add it to `registry.json` on the `main` branch so it can be invoked via a friendly alias by `just tc <alias>`.
5. **Syncing**: To get the latest base templates, sync from upstream `cc`, then run `just cc cascade` to auto-merge the upstream changes into your hybrid branches.
