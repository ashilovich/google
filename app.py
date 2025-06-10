import streamlit as st
import pandas as pd

st.title("Просмотр Google Sheets (публично)")

SHEET_ID = "ВСТАВЬ_СВОЙ_ID_ОТСЮДА"
SHEET_NAME = "Sheet1"  # Если лист называется иначе — поменяй!

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_csv(url):
    return pd.read_csv(url)

try:
    df = load_csv(csv_url)
    st.dataframe(df)
    # Поиск по комнате (если есть такая колонка)
    if "Room" in df.columns:
        room = st.text_input("Поиск по номеру комнаты")
        st.write(df[df["Room"].astype(str).str.contains(room, case=False)]) if room else None
except Exception as e:
    st.error("Ошибка загрузки данных: " + str(e))
