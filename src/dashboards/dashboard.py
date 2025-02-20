import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine
import pandas as pd
from constants.constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
from charts import line_chart


connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"

engine = create_engine(connection_string)


def load_data(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        df = df.set_index("timestamp")
        return df


count = st_autorefresh(interval=10 * 1000, limit=100, key="data_refresh")


def layout():
    df = load_data("SELECT * FROM ethereum;")

    st.markdown("# Coin data")
    st.markdown("Display live data from coinmarket API")
    st.markdown("Latest data")
    st.markdown("## Latest price in USD for Ethereum")

    st.dataframe(df.tail())
    price_chart = line_chart(x=df.index, y=df["price"], title="price USD")

    st.pyplot(price_chart)


if __name__ == "__main__":
    layout()
