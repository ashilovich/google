import streamlit as st
import pandas as pd

st.title("Просмотр данных из Google Sheets")

# Вставьте сюда ваш Google Sheet ID!
SHEET_ID = "ВСТАВЬТЕ_СВОЙ_ID_ТУТ"

# Обычно первый лист называется 'Sheet1', но иногда по-другому
SHEET_NAME = "Sheet1"  # при необходимости измените!

URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(URL)
    st.dataframe(df)
except Exception as e:
    st.error("Не удалось загрузить таблицу. Проверьте правильность ID, имени листа и настройки доступа.")
    st.text(str(e))

# Фильтр: поиск по комнате (если есть поле Room)
if 'Room' in df.columns:
    room = st.text_input("Поиск по комнате")
    if room:
        result = df[df['Room'].astype(str).str.contains(room, case=False)]
        st.write(result)
