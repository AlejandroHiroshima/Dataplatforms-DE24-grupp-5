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

connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"
engine = create_engine(connection_string)

def load_data(query):
    with engine.connect() as connection:
        result = pd.read_sql_query(
            text(query),
            connection
        )
        return result.set_index("Last updated")

count = st_autorefresh(interval=10 * 1000, limit=100, key="data_refresh")

def layout():
    try:
        df = load_data("""
            SELECT
                timestamp AS "Last updated",
                cmc_rank AS "#",
                name AS "Name", 
                symbol AS "Symbol",
                price AS "Current price",
                percent_change_1h AS "1h %",
                percent_change_24h AS "24h %",
                percent_change_30d AS "30d %"
            FROM top_100 
            ORDER BY cmc_rank ASC;
        """) 
 

        df["Current price"] = df["Current price"].round(2)
        df["1h %"] = df["1h %"].round(2)
        df["24h %"] = df["24h %"].round(2)
        df["30d %"] = df["30d %"].round(2) 

        st.image("kryptokollen.png", caption="Krypto", use_container_width=True)
        fear_and_greed_url = "https://alternative.me/crypto/fear-and-greed-index.png"
        st.image(fear_and_greed_url, caption="Fear and greed index for todays date", use_container_width=True)
        st.markdown("# Top 100 token by market cap:")
        st.dataframe(df) 

    except Exception as e:   
        st.error(f"Ett fel uppstod: {str(e)}")
        print(f"Detaljerat fel: {e}")

if __name__ == "__main__":
    layout()