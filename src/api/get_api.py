from src.constants.constants import COINMARKET_API
from requests import Session, TooManyRedirects, Timeout, HTTPError
import json
from pprint import pprint


def get_latest_coin_data(symbol="BTC"):
    api_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": COINMARKET_API,
    }

    parameters = {
        "symbol": symbol,
        "convert": "USD",
    }

    session = Session()

    session.headers.update(headers)

    try:
        response = session.get(api_url, params=parameters)
        response.raise_for_status()

        response_json = response.json()
        if "data" not in response_json:
            print(f"Unexpected API response: {response_json}")
            return None

        return response_json["data"].get(symbol, {})

    except (ConnectionError, Timeout, TooManyRedirects, HTTPError) as e:
        print(f"Request error: {e}")
        return None


# For testing
# test = get_latest_coin_data()
# pprint(test)
