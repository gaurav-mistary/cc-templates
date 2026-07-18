# Delegate all 'just cc <subcommand>' commands to the cc.just module
mod cc

# Build the Docker image. Defaults to prod.
# Usage: just docker-build dev
docker-build env="prod" *docker_args:
    docker build --build-arg BUILD={{env}} --progress=plain -t cc:latest {{docker_args}} .

# Run the Docker image as the cc-cli executable.
# Usage: just docker-run <volume_path> <cc-cli-args...>
# Example: just docker-run . init --pyv 3.12 --scratch
docker-run mount_path *args:
    #!/usr/bin/env bash
    if [ ! -d "{{mount_path}}" ]; then
        echo "Error: Directory '{{mount_path}}' does not exist. A valid path is required."
        exit 1
    fi
    # Resolve absolute path
    ABS_PATH=$(cd "{{mount_path}}" && pwd)
    
    # Automatically load .env file if it exists
    ENV_ARGS=""
    if [ -f "{{justfile_directory()}}/.env" ]; then
        ENV_ARGS="--env-file {{justfile_directory()}}/.env"
    fi

    # Run the container natively with SSH mounts
    docker run --rm -it $ENV_ARGS -v "$HOME/.ssh:/root/.ssh:ro" -v "$HOME/.gitconfig:/root/.gitconfig:ro" -v "$ABS_PATH:/output" -w /app cc:latest {{args}}
