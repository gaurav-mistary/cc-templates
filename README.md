# Custom Cookiecutter (CC) Engine

Welcome to the `cc` engine. This is a highly opinionated CLI and Git-based templating architecture designed to solve the "Cookiecutter drift" problem.

## The Problem
When you generate a project from a Cookiecutter template, it immediately becomes stale. When you maintain multiple variations of a template (e.g. a base webserver, a webserver with auth, a webserver with a specific database), maintaining the common denominator across all templates is a nightmare of duplication.

## The Solution: Branch-Based Inheritance
Instead of maintaining multiple folders of templates, we use **Git Branches** as the inheritance mechanism. 
- The `main` branch holds the `cc-cli` source code.
- A base technology (like `traefik`) is a branch directly off `main`.
- A feature addition (like adding HTTPS to Traefik) is a child branch off `traefik` called `traefik--secure`.
- By using our `cc cascade` tool, whenever you update the base `traefik` branch, Git automatically merges those changes down into `traefik--secure` and any other hybrid branches!

## The Architecture
We have decoupled the engine from the templates:
1. **`cc` (This Repo)**: Acts as the core engine. It contains the CLI python code, and the raw base building block branches (`py3.12`, `traefik`, `dockhand`).
2. **`cc-templates` (Your Fork)**: A fork of `cc` where you create your hybrid templates (e.g. `traefik--secure--dockhand`). You use GitHub to sync updates from `cc` into your fork, and then use `cc cascade` to propagate those updates to your hybrids.

## Usage

### The `tc` Just Module
The fastest way to use this system is via the `tc` (Template Create) module loaded in your `justfile`.

```bash
# Generate a project from an alias
just tc new secure-dockhand

# Generate into a specific directory
just tc new secure-dockhand /tmp/my-app
```

### The Registry Mapping
No one wants to type out internal branch names like `traefik--secure--dockhand`. The CLI supports a `registry.json` mapping.

You can host a `registry.json` locally at `~/.cc-registry.json` or host it on GitHub and expose it via a URL:

```json
{
  "secure-dockhand": "traefik--secure--dockhand",
  "web": "traefik--secure"
}
```

Tell the CLI to use it by setting the environment variable in your `.zshrc`:
```bash
export CC_REGISTRY="https://raw.githubusercontent.com/gaurav-mistary/cc-templates/main/registry.json"
```

## Internal CLI Commands (`cc-cli`)
If you want to use the raw CLI instead of the `just tc` wrappers:

```bash
# Cascade merges down the current branch tree
uv run cc-cli cascade

# Mix two branches dynamically in a temporary directory
uv run cc-cli mix py3.12 traefik -o /tmp/mixed-app

# Create a project from a template alias
uv run cc-cli template create secure-dockhand -o /tmp/app
```
