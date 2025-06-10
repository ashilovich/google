import streamlit as st
import pandas as pd

st.markdown(
    """
    <h1 style='text-align: center; color: #4F8BF9; font-size: 2.8em; font-weight: bold;'>
        LIST ROOMS GHM <span style="font-size:0.8em; color:#888;"></span>
    </h1>
    """,
    unsafe_allow_html=True
)

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
