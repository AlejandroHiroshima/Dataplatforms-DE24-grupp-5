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