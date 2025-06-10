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

def clean_df(df):
    bad_cols = [col for col in df.columns if col.startswith('Unnamed') or col == '']
    if bad_cols:
        df = df.drop(columns=bad_cols)
    return df.reset_index(drop=True)

df = clean_df(load_csv(csv_url))

unique_rooms = sorted(df["Room"].dropna().unique())
room_param = st.query_params.get("room", "")

if "room_select" not in st.session_state:
    st.session_state["room_select"] = room_param if room_param else ""

def clear_filter():
    st.session_state["room_select"] = ""
    if "room" in st.query_params:
        del st.query_params["room"]

from_url = bool(room_param)
show_filter_ui = not from_url

if show_filter_ui:
    if st.button("Обновить таблицу"):
        load_csv.clear()
        st.rerun()
    col1, col2 = st.columns([4, 1])
    with col1:
        selected_room = st.selectbox(
            "Выберите номер комнаты для поиска",
            [""] + unique_rooms,
            index=([""] + unique_rooms).index(st.session_state["room_select"])
            if st.session_state["room_select"] in unique_rooms else 0,
            key="room_select"
        )
    with col2:
        if st.session_state["room_select"]:
            st.button("Показать все комнаты", on_click=clear_filter)
    if st.session_state["room_select"]:
        st.query_params["room"] = st.session_state["room_select"]
    elif "room" in st.query_params:
        del st.query_params["room"]
    room = st.session_state["room_select"]
else:
    room = room_param

# Фильтрация по комнате
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

filtered_df = clean_df(filtered_df)
st.dataframe(filtered_df)

# === АНАЛИТИКА: ТОЛЬКО при переходе по ссылке ===
if from_url:
    # ТОП‑10 комнат с наибольшим количеством замечаний
    st.markdown("### ТОП‑10 комнат по количеству замечаний")
    top10_rooms = (
        df.groupby('Room')
        .size()
        .reset_index(name='Количество замечаний')
        .sort_values('Количество замечаний', ascending=False)
        .head(10)
    )
    st.dataframe(top10_rooms.reset_index(drop=True))

    # Итоговое количество замечаний (по всему DataFrame)
    st.markdown(
        f"**Общее количество всех замечаний:** <span style='color:#d02d2d;font-size:20px'>{df.shape[0]}</span>",
        unsafe_allow_html=True
    )

# QR‑код только при ручном выборе
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
    st.markdown(
        f'<a href="{qr_url}" target="_blank">Ссылка на поиск этой комнаты</a>',
        unsafe_allow_html=True
    )
