
import os
import streamlit as st
from openai import OpenAI, RateLimitError, APIError
from dotenv import load_dotenv
from characters import CHARACTERS

load_dotenv()

# Настройки страницы
st.set_page_config(
    page_title="Чат с персонажем",
    page_icon="📖"
)

st.title("📖 Поговори с литературным героем")

# Проверка API-ключа
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL")

if not api_key:
    st.error("Не найден API_KEY. Проверь файл .env")
    st.stop()

if not model:
    st.error("Не указана MODEL в файле .env")
    st.stop()

# Подключение OpenAI
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
)

# Выбор персонажа
name = st.sidebar.selectbox(
    "Персонаж",
    list(CHARACTERS.keys())
)

hero = CHARACTERS[name]

st.sidebar.markdown(f"**{hero['emoji']} {name}**")
st.sidebar.caption(hero["era"])

# Инициализация истории
key = f"msgs_{name}"

if key not in st.session_state:
    st.session_state[key] = [
        {"role": "system", "content": hero["system"]},
        {"role": "assistant", "content": hero["opener"]},
    ]

# Показ истории
for msg in st.session_state[key]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Ввод сообщения
if prompt := st.chat_input("Напишите реплику..."):

    st.session_state[key].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state[key],
                temperature=0.9,
                stream=True,
            )

            reply = st.write_stream(stream)

            st.session_state[key].append({
                "role": "assistant",
                "content": reply
            })

        except RateLimitError:
            st.error(
                "Превышена квота или закончились кредиты. "
                "Проверьте баланс Groq API."
            )

        except APIError as e:
            st.error(f"Ошибка OpenAI API: {e}")

        except Exception as e:
            st.error(f"Неожиданная ошибка: {e}")
