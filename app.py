import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO

SHEET_ID = "18HLTV6zdGRF_l6oZXxkO3LfDDPb92UrZVuFNbJFDVhc"
SHEET_NAME = "Snagging"

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# Загрузка таблицы
@st.cache_data
def load_csv(url):
    return pd.read_csv(url, encoding="utf-8")

df = load_csv(csv_url)

# Вывод заголовка красиво
st.markdown(
    "<h1 style='text-align: center; color: #4F8BF9;'>Просмотр комнат</h1>",
    unsafe_allow_html=True
)

# Фильтр по комнате
room = st.text_input("Введите номер комнаты для поиска")
filtered_df = df

if room:
    filtered_df = df[df["Room"].astype(str).str.contains(room, case=False)]
    st.write(f"Результаты для комнаты: **{room}**")

st.dataframe(filtered_df)

# Генерация QR-кода
if room:
    # Получаем полный URL текущей страницы с фильтром (Streamlit поддерживает параметры ?room=)
    base_url = st.experimental_get_query_params()
    app_url = st.secrets["app_url"] if "app_url" in st.secrets else "https://share.streamlit.io/ashilovich/google/main/app.py"
    qr_url = f"{app_url}?room={room}"

    # Генерируем изображение QR-кода
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    st.markdown("**Поделиться этой комнатой:**")
    st.image(buffered.getvalue(), caption="QR-код для ссылки")
    st.write(f"[Ссылка на поиск этой комнаты]({qr_url})")

    # Можно также автоматически устанавливать параметр в адресной строке
    st.experimental_set_query_params(room=room)
