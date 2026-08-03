# tc.just - Template Creation module
# Exposes short, user-friendly commands to create projects from templates

# The default output directory for generated projects
default_output := "~/projects/study"

# Create a project from any template alias in your registry
# Usage: just tc new <alias> [output_dir]
new alias output_dir=default_output *args:
    uv run python -m cc.cli template create {{alias}} --output-dir {{output_dir}} {{args}}

# --- Quick Shortcuts for Common Templates ---

# Create a secure dockhand setup
# Usage: just tc secure-dockhand
secure-dockhand output_dir=default_output *args:
    uv run python -m cc.cli template create secure-dockhand --output-dir {{output_dir}} {{args}}

# Create a basic webserver
# Usage: just tc webserver
webserver output_dir=default_output *args:
    uv run python -m cc.cli template create webserver --output-dir {{output_dir}} {{args}}

# Pass arbitrary raw commands to the template CLI
# Usage: just tc run --help
run *args:
    uv run python -m cc.cli template {{args}}
