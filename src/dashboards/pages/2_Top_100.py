import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine, text
import pandas as pd
from constants.constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
import time
from api.exchange_API import get_exchange_rates
import json
from dashboards.resources.charts import line_chart

fiat_currency = {
    "SEK": lambda: get_exchange_rates(base_currency="USD", rate="SEK"),
    "NOK": lambda: get_exchange_rates(base_currency="USD", rate="NOK"),
    "DKK": lambda: get_exchange_rates(base_currency="USD", rate="DKK"),
    "ISK": lambda: get_exchange_rates(base_currency="USD", rate="ISK"),
}

connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"
engine = create_engine(connection_string)
st.set_page_config(layout="wide")


def format_large_number(number):
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return f"{number:.2f}"


# Query funktioner:

# För grafen
def get_historical_data(coin_name):
    query = f"""
    SELECT timestamp,
           price as "Current price"
    FROM top_100 
    WHERE name = '{coin_name}' 
    ORDER BY timestamp ASC; 
    """
    with engine.connect() as connection:
        result = pd.read_sql_query(text(query), connection)
    return result

# För listan för de unika coins'en:
def get_coin_names():
    query = """ 
    SELECT DISTINCT ON (cmc_rank) name
    FROM top_100
    WHERE cmc_rank IS NOT NULL
    ORDER BY cmc_rank ASC, timestamp DESC 
    LIMIT 101; 
    """
    with engine.connect() as connection:
        result = pd.read_sql_query(text(query), connection)
        return result["name"].tolist()

# För top100 dataframen
def load_data(query):
    with engine.connect() as connection:
        result = pd.read_sql_query(text(query), connection)
        return result.set_index("#")


st_autorefresh(interval=60 * 1000, limit=100, key="data_refresh")


def layout():
    try:
        df = load_data(
            """
            SELECT DISTINCT ON (cmc_rank)
                cmc_rank AS "#",
                name AS "Name",
                symbol AS "Symbol", 
                price AS "Current price", 
                marketcap AS "Market Cap",
                percent_change_1h AS "1h %",
                percent_change_24h AS "24h %",
                percent_change_30d AS "30d %", 
                volume_24h AS "Volume traded last 24h" 
            FROM top_100 
            ORDER BY cmc_rank ASC, timestamp DESC
            LIMIT 101;
        """
        )

        col_left1, col_middle1, col_right1 = st.columns(3)
        with col_left1:
            pass
        with col_middle1:
            st.image("./resources/kryptokollen.png", width=2000)
            with col_right1:
                pass
        col_left2, col_middle2, col_right2 = st.columns(3)
        with col_left2:
            pass
        with col_middle2:
            fear_and_greed_url = (
                "https://alternative.me/crypto/fear-and-greed-index.png"
            )
            st.image(fear_and_greed_url, width=350)
        with col_right2:
            pass
        st.markdown("# Top 100 tokens by market cap:")
        st.dataframe(df, use_container_width=True, height=3535)

        fiat_currency_choice = st.selectbox(
            "Select fiat currency", fiat_currency.keys(), index=None
        )
        if fiat_currency_choice:
            available_coins = get_coin_names()
            select_coin = st.selectbox(
                "Choose cryptocurrency", options=available_coins, index=None
            )

            if select_coin:
                with st.spinner(f"Loading data for {select_coin}"):
                    time.sleep(2)

                    historical_data = get_historical_data(select_coin)

                    exchange_rate = fiat_currency[fiat_currency_choice]()

                    historical_data['Converted price'] = historical_data['Current price'] * exchange_rate

                    st.subheader(f"Price chart for {select_coin}")
                    price_chart = line_chart(
                        x=historical_data["timestamp"],
                        y=historical_data["Converted price"],
                        title=f"Price for {select_coin} in {fiat_currency_choice}",
                    )
                    st.pyplot(price_chart)

                    coin_query = f""" 
                    SELECT
                        cmc_rank AS "#",
                        name AS "Name", 
                        symbol AS "Symbol", 
                        price AS "Current price",
                        percent_change_1h AS "1h %",
                        percent_change_24h AS "24h %",
                        percent_change_30d AS "30d %", 
                        percent_change_60d as "60d %",
                        volume_24h AS "Volume traded last 24h",
                        marketcap AS "Market Cap",
                        fully_diluted_market_cap AS "Fully Diluted Market Cap",
                        total_supply AS "Total Supply",
                        max_supply AS "Max Supply",
                        tags AS "Coin Narrative"  
                    FROM top_100
                    WHERE name = '{select_coin}'
                    ORDER BY timestamp DESC
                    LIMIT 1; 
                    """

                    with engine.connect() as connection:
                        coin_data = pd.read_sql_query(
                            text(coin_query), connection
                        ).set_index("#")

                    coin_data = coin_data.fillna(0)

                    st.subheader(f"Information for: {select_coin}")

                
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        current_price = coin_data["Current price"].iloc[0]
                        converted_price = current_price * exchange_rate
                        st.metric(
                            "Current Price",
                            f"{fiat_currency_choice}: {converted_price:.4f}",
                        )
                    with col2:
                        volume = coin_data["Volume traded last 24h"].iloc[0]
                        converted_volume = volume * exchange_rate
                        st.metric(
                            "24h Volume",
                            f"{fiat_currency_choice}: {format_large_number(converted_volume)}"
                        )
                    with col3:
                        marketcap = coin_data["Market Cap"].iloc[0]
                        converted_marketcap = marketcap * exchange_rate
                        st.metric(
                            "Market Cap",
                            f"{fiat_currency_choice}: {format_large_number(converted_marketcap)}" 
                        )

                    col4, col5, col6 = st.columns(3)
                    with col4:
                        st.metric("1h Change", f"{coin_data['1h %'].iloc[0]:.2f}%")
                    with col5:
                        st.metric("24h Change", f"{coin_data['24h %'].iloc[0]:.2f}%")
                    with col6:
                        st.metric("30d Change", f"{coin_data['30d %'].iloc[0]:.2f}%")

                    col7, col8, col9 = st.columns(3)
                    with col7:
                        total_supply = coin_data["Total Supply"].iloc[0]
                        converted_total_supply = total_supply * exchange_rate
                        st.metric(
                            "Total Supply",
                            f"{fiat_currency_choice}: {format_large_number(converted_total_supply)}"
                        )
                    with col8:
                        max_supply = coin_data["Max Supply"].iloc[0]
                        converted_max_supply = max_supply * exchange_rate
                        st.metric(
                            "Max Supply",
                            f"{fiat_currency_choice}: {format_large_number(converted_max_supply)}" 
                            )
                        
                    with col9:
                        fully_diluted = coin_data["Fully Diluted Market Cap"].iloc[0]
                        converted_fully_diluted = fully_diluted * exchange_rate
                        st.metric(
                            "Fully Diluted Market Cap",
                            f"{fiat_currency_choice}: {format_large_number(converted_fully_diluted)}")
                            

                    tags_json = coin_data["Coin Narrative"].iloc[0]
                    tags = json.loads(tags_json) 
                    st.subheader("Coin Narrative")
                    for tag in tags:
                        if ("portfolio" in tag or "ecosystem" in tag or "exchange" in tag or "enterprise" in tag):
                            continue
                        if tag == "defi":
                            st.write("DeFi")
                        elif tag == "nft":
                            st.write("NFT's")
                        elif tag == "dao":
                            st.write("DAO")
                        elif "gaming" in tag:
                            st.write("Web3 gaming") 
                        elif tag == "pow":
                            st.write("Proof-Of-Work")
                        elif tag == "pos": 
                            st.write("Proof-Of-Stake")
                        elif "ai" in tag:
                            st.write("AI")
                        else:
                            st.write(tag.title())

    except Exception as e:
        st.error(f"Ett fel uppstod: {str(e)}")
        print(f"Detaljerat fel: {e}")


if __name__ == "__main__":
    layout()
