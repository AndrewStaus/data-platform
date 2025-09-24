{{-
    config(
        schema = "open_data",
        alias = "titanic",
        materialized = "view",
        meta = {
            "dagster": {
              "automation_condition": "eager"
            }
        }
    )
-}}

with titanic as (
    select * from {{ source("open_data", "titanic") }}
)

select
    pclass,
    name,
    sex,
    age,
    sibsp,
    parch,
    ticket,
    fare,
    cabin,
    embarked,
    boat,
    body,
    home_dest,
    survived::number(1, 0) survived
from titanic
