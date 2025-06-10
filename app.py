import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO

SHEET_ID = "18HLTV6zdGRF_l6oZXxkO3LfDDPb92UrZVuFNbJFDVhc"
SHEET_NAME = "Snagging"
APP_URL = "https://app-pvzv5rbkywwukbndmjmjvk.streamlit.app/"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_csv(url):
    return pd.read_csv(url, encoding="utf-8")

df = load_csv(csv_url)
unique_rooms = sorted(df["Room"].unique())

# Получаем фильтр из URL
room_param = st.query_params.get("room")
room_from_url = room_param if isinstance(room_param, str) or room_param is None else room_param[0]

# Управляем состоянием для сброса фильтра
if "room_select" not in st.session_state:
    st.session_state["room_select"] = room_from_url or ""

def reset_filter():
    st.session_state["room_select"] = ""
    st.query_params.clear()
    st.rerun()  # Убедись, что версия Streamlit поддерживает этот метод

col1, col2 = st.columns([4, 1])
with col1:
    selected_room = st.selectbox(
        "Выберите номер комнаты для поиска",
        [""] + unique_rooms,
        index=(unique_rooms.index(st.session_state["room_select"]) + 1) if st.session_state["room_select"] in unique_rooms else 0,
        key="room_select"
    )
with col2:
    if st.session_state["room_select"]:
        st.button("Показать все комнаты", on_click=reset_filter)

# Сохраняем фильтр в URL для глубокой ссылки
if st.session_state["room_select"]:
    st.query_params["room"] = st.session_state["room_select"]
elif "room" in st.query_params:
    del st.query_params["room"]

room = st.session_state["room_select"]

# Фильтрация данных
filtered_df = df[df["Room"].astype(str).str.strip().str.lower() == room.strip().lower()] if room else df

st.dataframe(filtered_df)

# QR-код и ссылка только при выборе комнаты
if room:
    qr_url = f"{APP_URL}?room={room}"
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    st.markdown("**Поделиться этой комнатой:**")
    st.image(buffered.getvalue(), caption="QR-код для ссылки")
    st.markdown(f'<a href="{qr_url}" target="_blank">Ссылка на поиск этой комнаты</a>', unsafe_allow_html=True)
