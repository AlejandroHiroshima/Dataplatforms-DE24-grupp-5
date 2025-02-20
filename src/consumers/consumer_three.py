from quixstreams import Application
# from pprint import pprint
import logging
import json
from quixstreams.sinks.community.postgresql import PostgreSQLSink
from constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

def extract_coin_data(message):
    latest_quote = message.get("quote", {}).get("USD", {})
    tags = message.get("tags", [])  # Om "tags" saknas får vi en tom lista
    tags = tags[:5] if len(tags) >= 5 else tags # längden på tags är 5, om den är större än eller = 5 från början, annars lika lång som den är (dvs 5 eller under 5)
    tags_json = json.dumps(tags)  #Konvertera till JSON-sträng
    return {
        "timestamp": message.get("last_updated"),
        "name": message.get("name"),
        "symbol": message.get("symbol"),
        "tags": tags_json,
        "marketcap": latest_quote.get("market_cap", 0),
        "fully_diluted_market_cap": latest_quote.get("fully_diluted_market_cap", 0),
        "percent_change_1h": latest_quote.get("percent_change_1h", 0),
        "percent_change_24h": latest_quote.get("percent_change_24h", 0),
        "percent_change_30d": latest_quote.get("percent_change_30d", 0),
        "percent_change_60d": latest_quote.get("percent_change_60d", 0),
        "percent_change_90d": latest_quote.get("percent_change_90d", 0),
        "price": latest_quote.get("price", 0),
        "tvl": latest_quote.get("tvl", 0),
        "volume_24h": latest_quote.get("volume_24h", 0),
        "volume_change_24h": latest_quote.get("volume_change_24h", 0),
        "total_supply": message.get("total_supply", 0),
        "cmc_rank": message.get("cmc_rank", 0),
        "max_supply": message.get("max_supply", 0)
    }


def create_postgres_sink():
    sink = PostgreSQLSink(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DBNAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        table_name="top_100",
        schema_auto_update=True,
    )

    return sink

def consumer_logging(log):
    logging.info("Consuming and sinking data")


def main():
    app = Application(
        broker_address="localhost:9092",
        consumer_group="top_100",
        auto_offset_reset="earliest",
    )
    coins_topic = app.topic(name="top_100_coins", value_deserializer="json")

    sdf = app.dataframe(topic=coins_topic)

    sdf = sdf.apply(extract_coin_data)

    postgres_sink = create_postgres_sink()

    sdf.sink(postgres_sink)

    sdf.update(consumer_logging)

    app.run()


if __name__ == "__main__":
    main()