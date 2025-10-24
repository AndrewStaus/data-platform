# Getting Started

## Setup

1. Open VS Code.
2. *Windows*: Install the `WSL` Extension.
3. *Windows*: Press `CTRL SHIFT P` and run `>WSL: Connect to WSL`.
4. Install the `Dev Containers` Extension.
5. *Windows*: Select `Clone Repository` to download to your Linux filesystem for better
performance.
6. Copy `.env.example` to `.env` and set your development credentials.
7. Press `CTRL SHIFT P` and run `>Dev Containers: Open in container`.
8. install Docker for WSL if prompted (This is the free community edition of docker).
9. Run `uv sync --all-packages` in the terminal.

*Note:* Windows Subsystem for Linux with an installed distribution is required for
developers using a Windows based local machine.

## Usage
- dbt-Fusion and its extensions will be automatically installed in the container.
You can run dbt models directly from VS Code.
- Snowflake extension is also installed to execute non-dbt scripts from VS Code.
- environments for libs, and packages/data_analytics will not be automatically
installed.  For a better development experience, you should run `uv sync` from within
the project directories to install the appropriate virtual environments.