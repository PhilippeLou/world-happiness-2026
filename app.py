import streamlit as st
from data_cleaning import load_and_clean_data

df = load_and_clean_data("data/world_happiness_2026.csv")

st.title("World Happiness Report 2026")
st.dataframe(df)