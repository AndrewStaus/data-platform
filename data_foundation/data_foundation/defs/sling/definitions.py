from dagster import Definitions
from dagster.components import definitions


@definitions
def defs() -> Definitions:
    """Returns set of definitions explicitly available and loadable by Dagster tools.
    Will be automatically dectectd and loaded by the load_defs function in the root
    definitions file.

    @definitions decorator will provides lazy loading so that the assets are only
    instantiated when needed.
    """
    from pathlib import Path

    from .factory import DagsterSlingFactory

    config_dir = Path(__file__).joinpath(*[".."], "sling").resolve()

    return DagsterSlingFactory.build_definitions(config_dir)
