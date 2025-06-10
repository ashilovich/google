import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import re

SHEET_ID = "18HLTV6zdGRF_l6oZXxkO3LfDDPb92UrZVuFNbJFDVhc"
SHEET_NAME = "Snagging"
APP_URL = "https://app-pvzv5rbkywwukbndmjmjvk.streamlit.app/"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_csv(url):
    return pd.read_csv(url, encoding="utf-8")

df = load_csv(csv_url)

# удаляем любые "Unnamed" столбцы и сбрасываем индекс
df = df.loc[:, ~df.columns.str.match('^Unnamed')]
df = df.reset_index(drop=True)
# убираем ещё раз если был явно индексный столбец
if '' in df.columns:
    df = df.drop(columns=[''])

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
    # Показываем кнопку обновления только здесь!
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

# ---- Фильтрация по комнате ----
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

# ======= АНАЛИТИКА ДЛЯ ПЕРЕХОДА ПО ССЫЛКЕ ========
if from_url and room and not filtered_df.empty:
    # 1. Этаж (B01-C-17 --> B01)
    match = re.match(r'^([^\s-]+)', str(room).strip())
    floor = match.group(1) if match else ""
    st.markdown(f"### Аналитика по этажу: **{floor}**")

    # 2. Подсчёт по комнатам этого этажа
    by_floor = df[df['Room'].astype(str).str.startswith(floor)]
    counts_by_room = (
        by_floor.groupby('Room')
        .size()
        .reset_index(name='Количество замечаний')
        .sort_values('Количество замечаний', ascending=False)
    )
    st.markdown("**Замечания по всем комнатам этажа:**")
    st.dataframe(counts_by_room.reset_index(drop=True))
    st.markdown(
        f"<div style='font-size:16px;margin:4px 0;'>"
        f"<b>Итого замечаний на этаже {floor}: </b>"
        f"<span style='color:#d02d2d;font-size:19px;'>{by_floor.shape[0]}</span></div>",
        unsafe_allow_html=True
    )

    # 3. Топ-10 комнат всего дома с наибольшим количеством замечаний
    top10_rooms = (
        df.groupby('Room')
        .size()
        .reset_index(name='Количество замечаний')
        .sort_values('Количество замечаний', ascending=False)
        .head(10)
    )
    st.markdown("### ТОП‑10 комнат с наибольшим числом замечаний:")
    st.dataframe(top10_rooms.reset_index(drop=True))

# ======= QR‑код только при ручном выборе =======
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
