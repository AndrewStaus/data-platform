from collections.abc import Generator
from typing import Any


def get_campaigns() -> Generator[list[dict[str, Any]], Any, None]:
    """A generator that will yield responses from a stub representing an api to
    download data from facebook ads.
    """

    response = [
        {
            "id": 90009,
            "name": "summer_sale",
            "start_date": "2024-06-01",
            "updated": "2025-07-02 21:14:03",
        },
        {
            "id": 80008,
            "name": "winter_sale",
            "start_date": "2024-01-01",
            "updated": "2025-07-02 21:14:03",
        },
        {
            "id": 70008,
            "name": "LAPTOP",
            "start_date": "2024-01-01",
            "updated": "2025-07-03 21:14:03",
        },
        {
            "id": 60008,
            "name": "greenfrog",
            "start_date": "2024-01-01",
            "updated": "2025-07-04 21:14:03",
        },
        {
            "id": 50008,
            "name": "blowout",
            "start_date": "2024-01-01",
            "updated": "2025-07-05 21:14:03",
        },
        {
            "id": 40008,
            "name": "raindays",
            "start_date": "2024-01-01",
            "updated": "2025-07-06 21:14:03",
        },
        {
            "id": 30008,
            "name": "powersale",
            "start_date": "2024-01-01",
            "updated": "2025-07-07 21:14:03",
        },
        {
            "id": 20008,
            "name": "sale11111",
            "start_date": "2024-01-01",
            "updated": "2025-07-08 21:14:03",
        },
        {
            "id": 10008,
            "name": "sale11112",
            "start_date": "2024-01-01",
            "updated": "2025-07-09 21:14:03",
        },
        {
            "id": 11008,
            "name": "sale11113",
            "start_date": "2024-01-01",
            "updated": "2025-07-10 21:14:03",
        },
        {
            "id": 12008,
            "name": "sale11114",
            "start_date": "2024-01-01",
            "updated": "2025-07-11 21:14:03",
        },
        {
            "id": 13008,
            "name": "sale11115",
            "start_date": "2024-01-01",
            "updated": "2025-07-12 21:14:03",
        },
        {
            "id": 14008,
            "name": "sale11116",
            "start_date": "2024-01-01",
            "updated": "2025-07-13 21:14:03",
        },
        {
            "id": 15008,
            "name": "sale11117",
            "start_date": "2024-01-01",
            "updated": "2025-07-14 21:14:03",
        },
        {
            "id": 16008,
            "name": "sale11118",
            "start_date": "2024-01-01",
            "updated": "2025-07-15 21:14:03",
        },
        {
            "id": 17008,
            "name": "sale11119",
            "start_date": "2024-01-01",
            "updated": "2025-07-16 21:14:03",
        },
        {
            "id": 18008,
            "name": "sale11110",
            "start_date": "2024-01-01",
            "updated": "2025-07-17 21:14:03",
        },
        {
            "id": 19008,
            "name": "sale11121",
            "start_date": "2024-01-01",
            "updated": "2025-07-18 21:14:03",
        },
        {
            "id": 11001,
            "name": "sale11122",
            "start_date": "2024-01-01",
            "updated": "2025-07-19 21:14:03",
        },
        {
            "id": 11002,
            "name": "sale11123",
            "start_date": "2024-01-01",
            "updated": "2025-07-20 21:14:03",
        },
        {
            "id": 11003,
            "name": "sale11124",
            "start_date": "2024-01-01",
            "updated": "2025-07-21 21:14:03",
        },
        {
            "id": 11004,
            "name": "sale11125",
            "start_date": "2024-01-01",
            "updated": "2025-07-22 21:14:03",
        },
        {
            "id": 11005,
            "name": "sale11126",
            "start_date": "2024-01-01",
            "updated": "2025-07-23 21:14:03",
        },
        {
            "id": 11006,
            "name": "sale11127",
            "start_date": "2024-01-01",
            "updated": "2025-07-24 21:14:03",
        },
        {
            "id": 66007,
            "name": "sale11128",
            "start_date": "2024-01-01",
            "updated": "2025-07-25 21:14:03",
        },
        {
            "id": 43008,
            "name": "sale11129",
            "start_date": "2024-01-01",
            "updated": "2025-07-26 21:14:03",
        },
        {
            "id": 76009,
            "name": "sale11131",
            "start_date": "2024-01-01",
            "updated": "2025-07-27 21:14:03",
        },
        {
            "id": 65008,
            "name": "sale11132",
            "start_date": "2024-01-01",
            "updated": "2025-07-28 21:14:03",
        },
        {
            "id": 54007,
            "name": "sale11133",
            "start_date": "2024-01-01",
            "updated": "2025-07-29 21:14:03",
        },
        {
            "id": 43006,
            "name": "sale11134",
            "start_date": "2024-01-01",
            "updated": "2025-07-31 21:14:03",
        },
        {
            "id": 32005,
            "name": "sale11135",
            "start_date": "2024-01-01",
            "updated": "2025-08-01 21:14:03",
        },
        {
            "id": 21004,
            "name": "sale11136",
            "start_date": "2024-01-01",
            "updated": "2025-08-02 21:14:03",
        },
        {
            "id": 54003,
            "name": "sale11137",
            "start_date": "2024-01-01",
            "updated": "2025-08-03 21:14:03",
        },
        {
            "id": 66002,
            "name": "sale11138",
            "start_date": "2024-01-01",
            "updated": "2025-08-04 21:14:03",
        },
        {
            "id": 77001,
            "name": "sale11139",
            "start_date": "2024-01-01",
            "updated": "2025-08-05 21:14:03",
        },
        {
            "id": 88044,
            "name": "sale11141",
            "start_date": "2024-01-01",
            "updated": "2025-08-06 21:14:03",
        },
        {
            "id": 99033,
            "name": "sale11142",
            "start_date": "2024-01-01",
            "updated": "2025-08-07 21:14:03",
        },
        {
            "id": 33220,
            "name": "sale11143",
            "start_date": "2024-01-01",
            "updated": "2025-08-08 21:14:03",
        },
    ]
    yield response
