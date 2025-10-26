"""Dagster definition entry point for orchestrating the example dbt project.

This module wires the dbt project metadata into the :class:`DagsterDbtFactory`
so that the resulting :class:`dagster.Definitions` object exposes assets, sensors,
and resources consistent with a real deployment.
"""

import os
from pathlib import Path

from dagster import Definitions
from dagster.components import definitions
from dagster_dbt import DbtProject

from .factory import Factory


@definitions
def defs() -> Definitions:
    """@definitions decorator will provides lazy loading so that the assets are only
    instantiated when needed. Will be automatically detected and loaded by the load_defs
    function in the root definitions file.
    
    Returns:
        dagster.Definitions: The definitions explicitly available and loadable by
            Dagster tools.
        
    """
    project_dir = Path(__file__).joinpath(*[".."] * 5, "dbt/").resolve()
    state_path = "state/"


    def dbt() -> DbtProject:
        """Instantiate a :class:`DbtProject` with environment-aware configuration.

        Returns:
            dagster_dbt.DbtProject: The fully configured dbt project instance that
                Dagster will interact with when executing assets. The helper runs
                ``prepare_if_dev`` to ensure the project is ready for local execution
                when targeting a development profile.
        """
        project = DbtProject(
            project_dir=project_dir,
            packaged_project_dir=project_dir,
            target=os.getenv("TARGET", "dev"),
            state_path=state_path,
            profile="dbt",
        )
        project.prepare_if_dev()
        return project
    
    return Factory.build_definitions(dbt)
