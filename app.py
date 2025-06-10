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
room_param = st.query_params.get("room", None)
by_url = room_param is not None

# --- Управляемое состояние selectbox ---
if 'room_select' not in st.session_state:
    st.session_state['room_select'] = ""

# Если в URL есть room и это не отражено в session_state — устанавливаем
if by_url and (st.session_state['room_select'] != room_param):
    st.session_state['room_select'] = room_param if isinstance(room_param, str) else room_param[0]
elif not by_url and st.session_state['room_select']:
    # Если params очищены, но в selectbox что-то есть — сбрасываем
    st.session_state['room_select'] = ""

show_input = not by_url

if show_input:
    col1, col2 = st.columns([4, 1])
    with col1:
        room = st.selectbox(
            "Выберите номер комнаты для поиска",
            [""] + unique_rooms,
            index=([""] + unique_rooms).index(st.session_state['room_select']) if st.session_state['room_select'] in unique_rooms else 0,
            key='room_select'
        )
    with col2:
        if st.session_state['room_select'] and st.button("Показать все комнаты"):
            # Сброс: очищаем всё
            st.query_params.clear()
            st.session_state['room_select'] = ""
            st.experimental_rerun()
    # Обновляем query params если выбрана комната
    if st.session_state['room_select']:
        st.query_params["room"] = st.session_state['room_select']
    elif "room" in st.query_params:
        del st.query_params["room"]
    room = st.session_state['room_select']
else:
    room = room_param if isinstance(room_param, str) else room_param[0]

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

if room and show_input:
    qr_url = f"{APP_URL}?room={room}"
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    st.markdown("**Поделиться этой комнатой:**")
    st.image(buffered.getvalue(), caption="QR-код для ссылки")
    # ССЫЛКА — новая вкладка!
    st.markdown(f'<a href="{qr_url}" target="_blank">Ссылка на поиск этой комнаты</a>', unsafe_allow_html=True)
