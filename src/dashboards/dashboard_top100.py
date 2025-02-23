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

#Query metoder
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