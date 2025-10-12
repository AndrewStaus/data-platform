"""Prepares workspace and runs dg dev."""
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
     set_cwd()
     sync_packages()
     dg_dev()

def run(command) -> None:
    """Executes a command and streams its output line by line."""
    with subprocess.Popen(command, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, bufsize=1) as process:
        for line in process.stdout: # type: ignore
            print(line.strip(), flush=True)

    if process.returncode != 0:
        print(f"Command exited with error code {process.returncode}", file=sys.stderr)

def set_cwd() -> None:
    """Set the current working directory to the workspace root so script can be
    run from any directory."""
    workspace_root = Path(__file__).parent.parent
    os.chdir(workspace_root)

def sync_packages() -> None:
    """Installs dependanices for all subpackages."""
    toml_paths = Path(__file__).parent.parent.glob("**/pyproject.toml")
    for toml_path in toml_paths:
            parents = [parent.name for parent in toml_path.parents]
            package_dir = toml_path.parent.resolve().as_posix()
            if ".venv" not in parents and "packages" in parents:
                run(["uv", "sync", "--directory", package_dir]) 

def dg_dev() -> None:
     """Runs the dg dev command"""
     run(["dg", "dev"])

if __name__ == "__main__":
     main()