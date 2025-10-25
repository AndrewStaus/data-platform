import requests


def fetch_transactions():
    """Fetch paginated transactions from API"""
    page = 1
    while True:
        response = requests.get(f"https://api.example.com/transactions?page={page}")
        data = response.json()
        if not data:
            break
        yield data
        page += 1
