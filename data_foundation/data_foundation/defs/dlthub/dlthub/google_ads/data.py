"""Stub datasets that emulate Google Ads API responses for demos and tests."""
from collections.abc import Callable, Generator
from typing import Any


def google_ads(endpoint: str) -> Callable[[], Generator[list[dict[str, Any]], Any]]:
    """Return a generator that yields sample payloads for the requested endpoint.

    Args:
        endpoint: Name of the Google Ads API endpoint to emulate.

    Returns:
        Callable[[], Generator[list[dict[str, Any]], Any, None]]: Zero-argument callable
        that yields batches of dictionaries representing API responses for the
        requested endpoint.

    Raises:
        KeyError: If the provided endpoint is not supported by the stub implementation.
    """

    if endpoint == "get_campaigns":

        def get_campaigns() -> Generator[list[dict[str, Any]], Any]:
            """Yield a canned list of campaign records with related criteria.

            Yields:
                list[dict[str, Any]]: Campaign objects that mimic the subset of fields
                commonly consumed downstream, including associated targeting
                ``criteria`` IDs for join operations.
            """
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

        def get_criterion() -> Generator[list[dict[str, Any]], Any]:
            """Yield mock targeting criterion records referenced by campaigns.

            Yields:
                list[dict[str, Any]]: Criterion dictionaries keyed by ``id`` along with
                ``type`` and ``value`` metadata for enrichment joins.
            """
            response = [
                {"id": 1, "type": "audience", "value": "summer_shoppers"},
                {"id": 2, "type": "age", "value": "20-35"},
            ]
            yield response

        return get_criterion

    else:
        raise KeyError(f"Endpoint '{endpoint}' is not implemented.")
