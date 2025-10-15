# analyics_utils/

Utilities for working with Snowflake and Snowpark easier in interactive jupyter
notebook sessions.

## Modules

- `snowpark`: Helpers that will initilize a snowpark session upon import and override
the `display` function in jupyer with a rich, and resource constrained
pygwalker display.