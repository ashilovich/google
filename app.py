import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO

SHEET_ID = "18HLTV6zdGRF_l6oZXxkO3LfDDPb92UrZVuFNbJFDVhc"
SHEET_NAME = "Sheet1"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_csv(url):
    return pd.read_csv(url, encoding="utf-8")

df = load_csv(csv_url)

# СЧИТЫВАЕМ фильтр из строки браузера при заходе по ссылке (streamlit>=1.32)
room_default = st.query_params.get("room", None)
if room_default:
    room_default = room_default if isinstance(room_default, str) else room_default[0]
else:
    room_default = ""

# Текстовое поле с подстановкой из параметра
room = st.text_input("Введите номер комнаты для поиска", value=room_default)

# Устанавливаем query параметр при фильтрации через UI и обновляем ссылку
st.query_params["room"] = room

filtered_df = df
if room:
    filtered_df = df[df["Room"].astype(str).str.contains(room, case=False)]
    st.write(f"Результаты для комнаты: **{room}**")

st.dataframe(filtered_df)

if room:
    # Формируем адрес текущего приложения без query
    app_url = st.secrets["app_url"] if "app_url" in st.secrets else st.request.url.split('?',1)[0]
    qr_url = f"{app_url}?room={room}"

    # Генерируем QR
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    st.markdown("**Поделиться этой комнатой:**")
    st.image(buffered.getvalue(), caption="QR-код для ссылки")
    st.write(f"[Ссылка на поиск этой комнаты]({qr_url})")
