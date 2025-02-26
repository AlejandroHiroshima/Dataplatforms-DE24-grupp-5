import streamlit as st

st.set_page_config(
    page_title="Kryptokollen Home",
    layout="centered",  # or "wide"
)

st.title("Welcome to Kryptokollen!")
st.write("**Note:** This is a work in progress. Features and data may change.")
st.write(
    """
    Explore various cryptocurrency dashboards using the sidebar links.
    - **ETH & UFD**: Check out Ethereum and Unicorn Fart Dust.
    - **Top 100**: Browse the top 100 tokens from CoinMarketCap.
    """
)
