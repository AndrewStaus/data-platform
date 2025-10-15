# data_platform_utils/

Utilities for common integration settings in Dagster across user code-locations.

## Modules

- `automation_conditions`: Automation condition objects that govern DAG execution
and scheduling.
- `helpers`: Factories for parsing dagster meta configurations and returning python
objects that can be understood by Dagster.  Also contains functions for resolving
database and schemas for given environments.
- `keyvault_stub`: A stub keyvault meant to simulate a hosted service.  This would be
replaced by an appropriate cloud secret keeper in a real deployment.
- `secrets`: A wrapper for the keyvault that allows for abstraction so that the
underlying service could be replaced.