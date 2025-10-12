"""Entry point for programmatically loading Dagster definitions for the project.

Dagster's component-based loader expects a function decorated with
``@dagster.components.definitions`` that returns the ``Definitions`` object to expose.
This module provides that hook and centralizes the logic that discovers assets,
resources, and schedules declared under :mod:`data_platform.defs`.
"""

from pathlib import Path
import warnings

import dagster as dg
from dagster.components import definitions

warnings.filterwarnings("ignore", category=dg.BetaWarning)
warnings.filterwarnings("ignore", category=UserWarning)


@definitions
def data_foundation() -> dg.Definitions:
    """Construct Dagster definitions from the ``data_foundation/defs`` package.

    Returns:
        dagster.Definitions: A ``Definitions`` instance containing every asset,
        resource, sensor, and schedule discovered under the ``defs`` folder relative
        to the project root. The loader mirrors Dagster's CLI ``defs`` semantics so
        end users receive the same set of assets whether they invoke the CLI or the
        Python API.
    """
    project_root = Path(__file__).joinpath(*[".."] * 2).resolve()
    
    return dg.load_from_defs_folder(project_root=project_root)
