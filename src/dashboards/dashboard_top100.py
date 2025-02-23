import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine, text
import pandas as pd
from constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
import time
from charts import line_chart

fiat_currency = {"SEK": 10, "NOK": 11, "DKK": 7, "ISK": 140}  # Fixa dessa sen

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

#Query funktioner
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
  
def load_data(query): 
    with engine.connect() as connection:
        result = pd.read_sql_query(text(query), connection)
        return result.set_index("#")
    
count = st_autorefresh(interval=60 * 1000, limit=100, key="data_refresh")


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

        df = df.iloc[1:].reset_index(drop=True)
        df.index = df.index + 1

        col_left1, col_middle1, col_right1 = st.columns(3)
        with col_left1:
            pass
        with col_middle1:
            st.image("kryptokollen.png", width=2000)
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

        #val av fiat-valuta (gör inget än)
        fiat_currency_choice = st.selectbox(
            "Select fiat currency", fiat_currency.keys(), index=None
        )
        if fiat_currency_choice:
            available_coins = get_coin_names()
            select_coin = st.selectbox(
                "Choose cryptocurrency",
                options=available_coins,
                index=None
            ) 

            if select_coin:
                with st.spinner(f"Loading data for {select_coin}"):
                    time.sleep(2)

                    historical_data = get_historical_data(select_coin)
                    st.subheader(f"Price chart for {select_coin}")
                    price_chart = line_chart(
                        x=historical_data["timestamp"],
                        y=historical_data["Current price"],
                        title=f"Price for {select_coin}"
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
                        st.metric(
                            "Current Price",
                            f"${coin_data['Current price'].iloc[0]:.4f}",
                        )
                    with col2:
                        st.metric(
                            "24h Volume",
                            format_large_number(
                                coin_data["Volume traded last 24h"].iloc[0]
                            ),
                        )
                    with col3:
                        st.metric(
                            "Market Cap",
                            format_large_number(coin_data["Market Cap"].iloc[0]),
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
                        st.metric(
                            "Total Supply",
                            format_large_number(coin_data["Total Supply"].iloc[0])
                        )
                    with col8:
                        st.metric(
                            "Max Supply",
                            format_large_number(coin_data["Max Supply"].iloc[0])
                        )
                    with col9: 
                        st.metric(
                            "Fully Diluted Market Cap",
                            format_large_number(
                                coin_data["Fully Diluted Market Cap"].iloc[0]
                            ),
                        )

                    st.subheader("Coin Narrative") 
                    st.write(coin_data["Coin Narrative"].iloc[0])

    except Exception as e:
        st.error(f"Ett fel uppstod: {str(e)}")
        print(f"Detaljerat fel: {e}") 


if __name__ == "__main__":
    layout() 
