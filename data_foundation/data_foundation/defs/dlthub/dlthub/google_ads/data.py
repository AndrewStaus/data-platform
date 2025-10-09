from collections.abc import Callable, Generator
from typing import Any


def google_ads(endpoint) -> Callable[[], Generator[list[dict[str, Any]], Any, None]]:
    """Return a generator that will yield responses from a stub representing an api to
    download data from google ads.
    """

    if endpoint == "get_campaigns":

        def get_campaigns() -> Generator[list[dict[str, Any]], Any, None]:
            response = [
                {
                    "id": 10001,
                    "name": "summer_sale",
                    "start_date": "2024-06-01",
                    "criteria": [{"id": 1}, {"id": 2}],
                },
                {
                    "id": 20002,
                    "name": "winter_sale",
                    "start_date": "2024-01-01",
                    "criteria": [{"id": 2}],
                },
            ]
            yield response

        return get_campaigns

    if endpoint == "get_criterion":

        def get_criterion() -> Generator[list[dict[str, Any]], Any, None]:
            response = [
                {"id": 1, "type": "audience", "value": "summer_shoppers"},
                {"id": 2, "type": "age", "value": "20-35"},
            ]
            yield response

        return get_criterion

    else:
        raise KeyError(f"Endpoint '{endpoint}' is not implemented.")
