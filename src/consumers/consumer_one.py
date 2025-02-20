from quixstreams import Application
from pprint import pprint
from quixstreams.sinks.community.postgresql import PostgreSQLSink
from constants.constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


def currency_rates(target_currency):
    exchange_rates = {
        "SEK": 10.69,
        "DKK": 6.66,
        "NOK": 10.37,
        "ISK": 140.21,
        "EUR": 0.89,
    }

    if target_currency in exchange_rates:
        return exchange_rates[target_currency]
    else:
        print(f"Currency {target_currency} not available")
        return None


def update_currency(price_in_usd, target_currency):
    exchange_rate = currency_rates(target_currency)
    if exchange_rate:
        return round(price_in_usd * exchange_rate, 4)
    else:
        print(f"Cannot update price for currency {target_currency} - Not available.")
        return None


def extract_coin_data(message):
    latest_quote = message["quote"]["USD"]
    price_usd = latest_quote["price"]
    price_sek = update_currency(price_usd, "SEK")
    price_dkk = update_currency(price_usd, "DKK")
    price_nok = update_currency(price_usd, "NOK")
    price_isk = update_currency(price_usd, "ISK")
    price_eur = update_currency(price_usd, "EUR")

    return {
        "coin": message["name"],
        "price_usd": price_usd,
        "price_sek": price_sek,
        "price_dkk": price_dkk,
        "price_nok": price_nok,
        "price_isk": price_isk,
        "price_eur": price_eur,
        "volume_24": latest_quote["volume_24h"],
        "updated": message["last_updated"],
        "market_rank": message["cmc_rank"],
        "percent_change_24h": latest_quote["percent_change_24h"],
        "total_supply": message["total_supply"],
        "infinite_supply": message["infinite_supply"],
        "date_added": message["date_added"],
    }


def create_postgres_sink():
    sink = PostgreSQLSink(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DBNAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        table_name="ethereum",
        schema_auto_update=True,
    )

    return sink


def main():
    app = Application(
        broker_address="localhost:9092",
        consumer_group="eth_group",
        auto_offset_reset="earliest",
    )
    coins_topic = app.topic(name="eth", value_deserializer="json")

    sdf = app.dataframe(topic=coins_topic)

    sdf = sdf.apply(extract_coin_data)

    postgres_sink = create_postgres_sink()

    sdf.sink(postgres_sink)

    sdf.update(lambda transformed_data: pprint(transformed_data))

    app.run()


if __name__ == "__main__":
    main()
