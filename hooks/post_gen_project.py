#!/usr/bin/env python3
import os
import subprocess
import sys


def main():
    dashboard_user = "{{ cookiecutter.dashboard_user }}"
    dashboard_password = "{{ cookiecutter.dashboard_password }}"

    # Check if the user entered the default or an empty password. If so, skip hashing or error out.
    if not dashboard_password or dashboard_password == "YOUR_SUPER_SECRET_PASSWORD":
        print("WARNING: You are using the default password for the Traefik dashboard.")

    print(f"Generating bcrypt hash for user '{dashboard_user}' using docker...")

    try:
        # Run the docker command to generate the hash
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "httpd:2.4-alpine",
                "htpasswd",
                "-nbB",
                dashboard_user,
                dashboard_password,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Output is like: admin:$2y$05$xxxxxxxxxxxxxxx\n
        # We need to extract the hash part.
        output = result.stdout.strip()
        if ":" in output:
            generated_hash = output.split(":", 1)[1]
        else:
            generated_hash = output

        # IMPORTANT: In docker-compose.yml, '$' must be escaped as '$$'
        escaped_hash = generated_hash.replace("$", "$$")

        # Path to docker-compose.yml (since this script runs inside the generated project directory)
        compose_file = "docker-compose.yml"

        if not os.path.exists(compose_file):
            print(f"ERROR: {compose_file} not found in {os.getcwd()}")
            sys.exit(1)

        with open(compose_file, "r") as f:
            content = f.read()

        # Replace the placeholder with the escaped hash
        new_content = content.replace("__DASHBOARD_PASSWORD_HASH__", escaped_hash)

        with open(compose_file, "w") as f:
            f.write(new_content)

        print("Successfully injected hashed password into docker-compose.yml")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to run docker command: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
