"""Utility helpers for retrieving exchange rate data from the sample API.

The helpers return callables compatible with dltHub loaders. Each generator lazily
requests JSON pages so Dagster assets can stream data without loading all responses
into memory at once.
"""

from collections.abc import Callable, Generator
from typing import Any

import requests


def get_exchange_rate(currency: str) -> Callable[[], Any]:
    """Return a generator that yields paginated currency exchange rate responses.

    Args:
        currency: Three-letter ISO currency code identifying the conversion table to
            fetch.

    Returns:
        Callable[[], Generator[Any, Any, None]]: A zero-argument callable that yields
        successive API responses encoded as Python dictionaries. The callable matches
        dlt's expectation for data loader functions.
    """

    uri = (
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api"
        "@latest"
        "/v1/"
        f"currencies/{currency}.json"
    )

    def exchange_api() -> Generator[Any, Any]:
        """Fetch the first API page and continue following pagination links.

        Yields:
            dict[str, Any]: Parsed JSON responses containing currency conversion rates
            plus pagination metadata. The generator stops when the API no longer
            provides a ``next_page`` URL.
        """
        response = requests.get(uri)
        yield response.json()
        while next_uri := response.json().get("next_page"):
            response = requests.get(next_uri)
            yield response.json()

    return exchange_api


if __name__ == "__main__":
    get_ex = get_exchange_rate("usd")
    for x in get_ex():
        print(x)
