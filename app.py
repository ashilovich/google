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

room_param = st.query_params.get("room")
# ---------------------------------
# --- **КНОПКА СБРОСА ФИЛЬТРА** ---
# ---------------------------------
if "clear_filter" not in st.session_state:
    st.session_state["clear_filter"] = False

# При нажатии кнопки: очищаем фильтр, query params и session_state, делаем rerun
def clear_filter():
    st.session_state["room_select"] = ""
    st.session_state["clear_filter"] = True
    if "room" in st.query_params:
        del st.query_params["room"]
    st.experimental_rerun()

# ------------------------------------------
# --------- ОСНОВНОЙ ФИЛЬТР UI -------------
# ------------------------------------------
from_url = room_param is not None

if from_url:
    current_room = room_param if isinstance(room_param, str) else room_param[0]
    # показываем просто результат, без фильтров/кнопок
    show_filter_ui = False
else:
    show_filter_ui = True
    if "room_select" not in st.session_state or st.session_state["clear_filter"]:
        st.session_state["room_select"] = ""
        st.session_state["clear_filter"] = False

    col1, col2 = st.columns([4,1])
    with col1:
        room_choose = st.selectbox(
            "Выберите номер комнаты для поиска",
            [""] + unique_rooms,
            key="room_select"
        )
    with col2:
        # Кнопка сброса появляется, только если что-то выбрано
        if st.session_state["room_select"]:
            st.button("Показать все комнаты", on_click=clear_filter)
    current_room = st.session_state["room_select"]
    # Синхронизируем URL параметр (для QR/ссылки), если выбран фильтр
    if current_room:
        st.query_params["room"] = current_room
    elif "room" in st.query_params:
        del st.query_params["room"]

# ----------------------
# --- ФИЛЬТРАЦИЯ -------
# ----------------------
if current_room:
    filtered_df = df[df["Room"].astype(str).str.strip().str.lower() == current_room.strip().lower()]
    num_remarks = len(filtered_df)
    st.markdown(
        f'<div style="font-size:20px; font-weight:bold;">'
        f'Результаты для комнаты: <span style="color:#3766bf;">{current_room}</span></div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:18px; margin-bottom:8px;">'
        f'Количество замечаний: <span style="color:#d02d2d;">{num_remarks}</span></div>',
        unsafe_allow_html=True)
else:
    filtered_df = df

st.dataframe(filtered_df)

# QR и ссылка только при ручном выборе через фильтр
if current_room and show_filter_ui:
    qr_url = f"{APP_URL}?room={current_room}"
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    st.markdown("**Поделиться этой комнатой:**")
    st.image(buffered.getvalue(), caption="QR-код для ссылки")
    st.markdown(f'<a href="{qr_url}" target="_blank">Ссылка на поиск этой комнаты</a>', unsafe_allow_html=True)
