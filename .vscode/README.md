# .vscode

This directory contains configuration files specific to Visual Studio Code for this project. These settings help ensure a consistent development environment for all contributors and optimize the VS Code experience.

## Purpose

- **Consistency**: Ensures all developers work with the same editor settings and
recommended extensions, reducing "works on my machine" issues.
- **Efficiency**: Provides predefined debugging configurations and tasks, streamlining
common development workflows.
- **Onboarding**: Makes it easier for new contributors to set up their development
environment by automatically suggesting essential tools and configurations.

## Contents

- **`settings.json`**: Workspace-specific settings that override or extend user-level
VS Code settings. This can include formatting rules, editor behavior, and extension
configurations.
- **`extensions.json`**: Recommended extensions for this project. VS Code will prompt
users to install these extensions upon opening the workspace, ensuring everyone has the
necessary tools.
- **`launch.json`**: Debugging configurations for various parts of the project. This
file defines how to start and attach debuggers for different runtimes or test suites.
- **`tasks.json`**: Custom build or utility tasks that can be run directly from VS Code.
This can include compiling code, running tests, or executing scripts.
- **`.code-snippets`**: Code snippets that can be shared between developers to increase
efficiency.

## Important Notes

-   **Avoid Sensitive Information**: Do not store sensitive information (e.g., API keys,
passwords) directly in these configuration files. Use environment variables or other
secure methods for managing secrets.
-   **Customization**: While these settings provide a baseline, individual developers
can still customize their personal VS Code settings (user settings) without affecting
the project's shared configurations.