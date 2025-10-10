import requests

# http://127.0.0.1:63446/assets/facebook_ads/src/campaigns

DAGSTER_WEBSERVER_HOST = "http://127.0.0.1:63446"
DAGSTER_WEBSERVER_HOST = "http://127.0.0.1:3000"
ASSET_KEY = "exchange_rate / src / usd".replace(" ", "")

external_asset_keys = [
    "accounts_db / src / accounts",
    "adobe_experience / src / app_hits",
    "adobe_experience / src / web_hits",
    "entity_resolution / src / individual_party_keys",
    "exchange_rate / src / cad",
    "exchange_rate / src / usd",
    "exchange_rate / src / usd",
    "facebook_ads / src / campaigns",
    "google_ads / src / campaigns",
    "google_ads / src / criterion",
    "inventory_db / src / products",
    "transaction_db / src / transactions",
]

for asset_key in external_asset_keys:
    asset_key = asset_key.replace(" ", "")
    url = f"{DAGSTER_WEBSERVER_HOST}/report_asset_materialization/{asset_key}"
    response = requests.request("POST", url)
    response.raise_for_status()
