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

# 1. Получаем фильтр из url
room_param = st.query_params.get("room")
from_url = room_param is not None
room_from_url = room_param if isinstance(room_param, str) or room_param is None else room_param[0]

# 2. Управляем session_state для корректного сброса
if "room_select" not in st.session_state:
    # Если зашли по прямой ссылке — вставить значение в состояние
    st.session_state["room_select"] = room_from_url or ""
if "reset_box" not in st.session_state:
    st.session_state["reset_box"] = False

def reset_filter():
    st.session_state["room_select"] = ""
    if "room" in st.query_params:
        del st.query_params["room"]
    st.session_state["reset_box"] = True  # Флаг для чистого сброса box!
    st.experimental_rerun()

show_filter_ui = not from_url

if show_filter_ui:
    col1, col2 = st.columns([4, 1])
    with col1:
        # Принудительный сброс selectbox до пустого на reset_box=True
        index = 0
        if st.session_state["room_select"] in unique_rooms:
            index = unique_rooms.index(st.session_state["room_select"]) + 1
        # ВАЖНО: при reset_box=True всегда index=0!
        if st.session_state["reset_box"]:
            index = 0
            st.session_state["reset_box"] = False  # Сброшено!
        selected_room = st.selectbox(
            "Выберите номер комнаты для поиска",
            [""] + unique_rooms,
            index=index,
            key="room_select"
        )
    with col2:
        if st.session_state["room_select"]:
            st.button("Показать все комнаты", on_click=reset_filter)

    # Сохраняем фильтр в URL query params для QR/глубокой ссылки
    if st.session_state["room_select"]:
        st.query_params["room"] = st.session_state["room_select"]
    elif "room" in st.query_params:
        del st.query_params["room"]

    room = st.session_state["room_select"]
else:
    room = room_from_url

# 3. Фильтрация
if room:
    filtered_df = df[df["Room"].astype(str).str.strip().str.lower() == room.strip().lower()]
    num_remarks = len(filtered_df)
    st.markdown(
        f'<div style="font-size:20px; font-weight:bold;">'
        f'Результаты для комнаты: <span style="color:#3766bf;">{room}</span></div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:18px; margin-bottom:8px;">'
        f'Количество замечаний: <span style="color:#d02d2d;">{num_remarks}</span></div>',
        unsafe_allow_html=True)
else:
    filtered_df = df

st.dataframe(filtered_df)

# 4. QR и ссылка только при выборе комнат в UI
if room and show_filter_ui:
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
