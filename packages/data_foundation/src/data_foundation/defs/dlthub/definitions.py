"""Resource definitions for dltHub integrations."""
import os
from pathlib import Path

from dagster import Definitions
from dagster.components import definitions
from data_platform_utils.secrets import set_dlt_credentials

from .factory import Factory


@definitions
def defs() -> Definitions:
    """Instantiate the dltHub resources required by the Dagster definitions.

    Returns:
        dagster.Definitions: Definitions exposing the ``dlt`` resource configured with
            credentials sourced from the local key vault stub. The helper ensures
            environment variables expected by dlt are populated before constructing the
            resource.
    """
    set_dlt_credentials()

    os.environ["ENABLE_DATASET_NAME_NORMALIZATION"] = "false"
    
    # Resolve the root folder containing dlt configuration files and scripts.
    config_dir = Path(__file__).joinpath(*[".."], "dlthub").resolve()

    return Factory.build_definitions(config_dir)
