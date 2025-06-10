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

# Проверяем, есть ли фильтр в адресе
url_room_param = st.query_params.get("room")
by_url = url_room_param is not None

# Логика выбора комнаты
if by_url:
    room = url_room_param if isinstance(url_room_param, str) else url_room_param[0]
    show_input = False
else:
    show_input = True
    room = st.selectbox("Выберите номер комнаты для поиска", [""] + unique_rooms)
    # Если пользователь выбрал, записываем параметр в URL, иначе удаляем
    if room:
        st.query_params["room"] = room
    elif "room" in st.query_params:
        del st.query_params["room"]

# Фильтрация
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

# Кнопка "Показать все комнаты" — только если фильтр не активен (только на исходной, без выбора)
# Теперь — кнопка вообще не выводится при отфильтрованном списке
# QR — только при фильтрации через интерфейс
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
