import os
from pathlib import Path

from dagster import Definitions
from dagster.components import definitions
from dagster_dbt import DbtProject

from .factory import DagsterDbtFactory


@definitions
def defs() -> Definitions:
    """Returns set of definitions explicitly available and loadable by Dagster tools.
    Will be automatically dectectd and loaded by the load_defs function in the root
    definitions file.

    @definitions decorator will provides lazy loading so that the assets are only
    instantiated when needed.
    """
    project_dir = Path(__file__).joinpath(*[".."] * 4, "dbt/").resolve()
    state_path = "state/"


    # .\.venv\Lib\site-packages\dagster_dbt\asset_utils.py
    # added: if unique_id in child_map.keys():
    # on line 816.  As of dbt fusion 2.09 the child map
    # does not poulate keys for assets if the asset has no children
    # resulting in key error when loading definitions.
    def dbt() -> DbtProject:
        project = DbtProject(
            project_dir=project_dir,
            target=os.getenv("TARGET", "dev"),
            state_path=state_path,
            profile="dbt",
        )
        # if os.getenv("TARGET") == "dev":
        project.prepare_if_dev()
        return project

    return DagsterDbtFactory.build_definitions(dbt)
