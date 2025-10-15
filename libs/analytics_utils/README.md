# analytics_utils/

Utilities for working with Snowflake and Snowpark easier in interactive jupyter
notebook sessions.

## Modules

- `snowpark`: Helpers that will initialize a snowpark session upon import and override
the `display` function in jupyter with a rich, and resource constrained
pygwalker display.