import streamlit as st
import pandas as pd
import numpy as np

st.title('General Election')

DATA_PATH='notebooks/GE_sdata.csv'

@st.cache
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

df = load_data()

st.dataframe(df)