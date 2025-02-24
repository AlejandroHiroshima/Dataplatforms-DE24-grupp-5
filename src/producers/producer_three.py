import time
from quixstreams import Application
from api.get_api import get_top_100
import json
from pprint import pprint
import logging


app = Application(broker_address="localhost:9092", consumer_group="top_100")
coins_topic = app.topic(name="top_100_coins", value_serializer="json")

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)



def main():
    logger.info("Starting cryptocurrency data producer")
    with app.get_producer() as producer:
        while True:
            try:
                coin_latest = get_top_100()
                if not coin_latest:
                    logger.error("Failed to fetch cryptocurrency data")
                    continue

                for coin in coin_latest["data"]:
                    kafka_message = coins_topic.serialize(
                        key= coin["symbol"],
                        value=coin  
                        )

                    logger.info(
                        f"Producing event - Timestamp: {kafka_message.key}, Coin: {coin['symbol']}"
                        )

                    producer.produce(
                        topic=coins_topic.name,
                        key=kafka_message.key,
                        value=kafka_message.value 
                        )

            except Exception as e: 
                logger.error(f"Error in main loop: {str(e)}", exc_info=True)
                
            time.sleep(60)

if __name__ == "__main__":
    main() 

