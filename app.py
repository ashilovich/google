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

# Получаем параметр из URL (если переход по ссылке)
url_room_param = st.query_params.get("room", None)
if url_room_param:
    room_default = url_room_param if isinstance(url_room_param, str) else url_room_param[0]
    show_input = False
else:
    room_default = ""
    show_input = True

# ----- КНОПКА СБРОСА ------
reset = False
if not show_input:
    # при переходе по ссылке с фильтром — покажем кнопку
    reset = st.button("Показать все комнаты")
    if reset:
        # Очищаем фильтр из query_params и перезапускаем страницу
        st.query_params.clear()
        st.experimental_rerun()

# ----- ПОЛЕ ДЛЯ ВВОДА ФИЛЬТРА -----
if show_input:
    col1, col2 = st.columns([4,1])
    with col1:
        room = st.text_input("Введите номер комнаты для поиска", value=room_default)
    with col2:
        if st.button("Сбросить фильтр"):
            st.query_params.clear()
            st.experimental_rerun()
    st.query_params["room"] = room
else:
    room = room_default

# ---- ФИЛЬТРУЕМ ТОЛЬКО ПО ТОЧНОМУ СОВПАДЕНИЮ ----
if room.strip():
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

# Показываем QR только если пользователь фильтрует самостоятельно, а не по ссылке
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
    st.write(f"[Ссылка на поиск этой комнаты]({qr_url})")
