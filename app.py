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

# Получаем параметр из URL (если человек зашел по ссылке с фильтром)
url_room_param = st.query_params.get("room", None)
if url_room_param:
    # Стримлит может возвращать либо строку, либо список – берем строку
    room_default = url_room_param if isinstance(url_room_param, str) else url_room_param[0]
else:
    room_default = ""

# Поле для ручного поиска
room = st.text_input("Введите номер комнаты для поиска", value=room_default)
# Сохраняем параметр в адресной строке
st.query_params["room"] = room

# Фильтрация данных
if room:
    filtered_df = df[df["Room"].astype(str).str.contains(room, case=False)]
    st.write(f"Результаты для комнаты: **{room}**")
else:
    filtered_df = df

st.dataframe(filtered_df)

# Показываем QR только если пользователь фильтрует самостоятельно, а не по ссылке
if room and not url_room_param:
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
