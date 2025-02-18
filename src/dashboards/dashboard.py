import streamlit
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine
import pandas as pd
from src.constants.constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

#! Stoped at 9:22

# First run dashboard with pythom -m src...dashboard to load data.
# Then run streamlit with python -m streamlit run src...dashboard.py or without

connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"

engine = create_engine(connection_string)


#! We can move the load to otner place if we want.
# Runs wehen we load dashboard module.
def load_data(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        df = df.set_index("timestamp")
        return df


def layout():
    df = load_data("SELECT * FROM ethereum;")

    st.markdown("# Coin data")
    st.markdown("# Display live data from coinmarket API")
    st.markdown("# Latest data")

    st.dataframe(df.tail())
