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
import matplotlib.pyplot as plt
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