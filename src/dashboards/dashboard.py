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


connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"
engine = create_engine(connection_string)


def format_large_number(number):
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return f"{number:.2f}"


def load_data(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")
        return df


st_autorefresh(interval=10 * 1000, limit=100, key="data_refresh")


def layout():
    st.title("Crypto Dashboard: Ethereum & Unicorn Fart Dust")

    df_eth = load_data("SELECT * FROM ethereum;")
    df_ufd = load_data("SELECT * FROM unicorn_fart_dust")

    currency = st.selectbox(
        "Select Currency", ["USD", "SEK", "DKK", "NOK", "ISK", "EUR"]
    )
    price_col = f"price_{currency.lower()}"

    # Display metrics
    st.subheader("Latest Prices and Stats")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("ETH Price", f"{df_eth[price_col].iloc[-1]:.2f} {currency}")
        st.metric("24h Volume", format_large_number(df_eth["volume_24"].iloc[-1]))
        st.metric("24h Change (%)", f"{df_eth['percent_change_24h'].iloc[-1]:.2f}%")

    with col2:
        st.metric("UFD Price", f"{df_ufd[price_col].iloc[-1]:.2f} {currency}")
        st.metric("24h Volume", format_large_number(df_ufd["volume_24"].iloc[-1]))
        st.metric("24h Change (%)", f"{df_ufd['percent_change_24h'].iloc[-1]:.2f}%")

    st.subheader("Price Trends")
    col3, col4 = st.columns(2)

    with col3:
        st.line_chart(df_eth[price_col], height=300)

    with col4:
        st.line_chart(df_ufd[price_col], height=300)


    with st.expander("Detailed ETH Data"):
        st.dataframe(df_eth.tail(10))

    with st.expander("Detailed UFD Data"):
        st.dataframe(df_ufd.tail(10))


# Run the dashboard
if __name__ == "__main__":
    layout()
