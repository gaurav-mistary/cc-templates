# Run cascade with standard merge strategy
cascade *args:
    uv run python -m cc.cli cascade {{args}}

# Catch-all for any other raw cc-cli commands
run *args:
    uv run python -m cc.cli {{args}}
