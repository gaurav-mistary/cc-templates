# Run cascade with standard merge strategy
cascade *args:
    uv run python -m cc.cli cascade {{args}}

create *args:
    uv run python -m cc.cli create {{args}}

# Catch-all for any other raw cc-cli commands
run *args:
    uv run python -m cc.cli {{args}}
