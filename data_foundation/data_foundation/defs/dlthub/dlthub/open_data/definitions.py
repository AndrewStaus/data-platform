# import dlt
# from dagster import Definitions
# from dagster.components import definitions


# @definitions
# def defs() -> Definitions:
#     from ...factory import ConfigurableDltResource, DagsterDltFactory
#     from .data import titanic

#     resources = [
#         ConfigurableDltResource.config(
#             dlt.resource(
#                 titanic,
#                 name="open_data.titanic",
#                 table_name="titanic",
#                 write_disposition="replace",
#             ),
#             kinds={"api"},
#             meta={
#                 "dagster": {
#                     "automation_condition": "missing_or_changed"
#                 }
#             },
#         )
#     ]
#     return DagsterDltFactory.build_definitions(tuple(resources))
