import streamlit as st
import pandas as pd

st.title("Просмотр Google Sheets (публично)")

SHEET_ID = "18HLTV6zdGRF_l6oZXxkO3LfDDPb92UrZVuFNbJFDVhc"
SHEET_NAME = "Snagging"

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_csv(url):
    try:
        return pd.read_csv(url, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(url, encoding="cp1251")

try:
    df = load_csv(csv_url)
    st.dataframe(df)
    if "Room" in df.columns:
        room = st.text_input("Поиск по номеру комнаты")
        if room:
            st.write(df[df["Room"].astype(str).str.contains(room, case=False)])
except Exception as e:
    st.error("Ошибка загрузки данных: " + str(e))
