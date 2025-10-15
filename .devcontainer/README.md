# .devcontainer/

Configuration files for setting up a standardized and reproducible development
environment using VS Code Dev Containers. 

## Purpose

Ensures that all developers working on this project have the same tools, dependencies,
and settings, regardless of their local machine configuration.

## Contents

- **`devcontainer.json`**: This is the primary configuration file for the Dev Container.
It defines:
        - The base Docker image or Dockerfile to use.
        - Extensions to install in VS Code within the container.
        - Settings to apply to VS Code within the container.
        - Ports to forward.
        - Post-create commands to run after the container is built.
        - Features to include (e.g., `git`, `docker`, specific language runtimes).
-   **`Dockerfile`**: If present, this file defines a custom Docker image used as the
base for the Dev Container, allowing for more specific environment customization beyond
what `devcontainer.json` offers.
-   **`docker-compose.yml` (optional)**: Used for multi-container setups, defining how
multiple services interact within the development environment.

## Usage

1. **Install Docker**: Ensure Docker CE or Docker Desktop is installed and running on
your local machine or in your WSL distribution.
2. **Install VS Code**: If you don't already have it, install Visual Studio Code.
3. **Install Dev Containers Extension**: Install the "Dev Containers" extension in VS
Code.
4. **Open in Container**:
    -   Open this project folder in VS Code.
    -   VS Code should prompt you to "Reopen in Container". Click this option.
    -   Alternatively, open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P) and run
    the command `Dev Containers: Reopen in Container`.

VS Code will then build the container (if it's the first time) and connect to it,
providing you with the configured development environment.

## Customization and Maintenance

- **Modifying the Environment**: Adjust `devcontainer.json` to change VS Code
settings, install new extensions, or modify port forwarding.
- **Updating Dependencies**: If a `Dockerfile` is used, modify it to update system-level
dependencies or install new software.
- **Rebuilding the Container**: After making changes to `devcontainer.json` or
`Dockerfile`, you may need to rebuild the container. Open the Command Palette and run
`Dev Containers: Rebuild Container`.

## Troubleshooting

- **Container Fails to Build**: Check the Docker logs for errors during the build
process.
- **Extensions Not Loading**: Ensure the extensions are correctly listed in
`devcontainer.json` and that the container has been rebuilt after changes.
- **Performance Issues**: Consider optimizing your `Dockerfile` or `devcontainer.json`
for smaller image sizes and faster build times.