import streamlit as st
import subprocess
import sys

# Автоматическая установка необходимых библиотек при первом запуске
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    from langchain_openai import ChatOpenAI
except ImportError:
    install("langchain-community")
    install("langchain-openai")
    install("duckduckgo-search")
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    from langchain_openai import ChatOpenAI

st.set_page_config(page_title="Юридические Субагенты", layout="wide")
st.title("⚖️ Дашборд Юридических Субагентов")

api_key = st.sidebar.text_input("Введите ключ OpenAI / DeepSeek API", type="password")

if api_key:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
    search = DuckDuckGoSearchAPIWrapper()

    user_input = st.text_area("Описание юридической ситуации:", height=100)

    if st.button("🚀 Запустить субагентов"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🔍 1. Поисковик")
            with st.spinner("Ищу законы в сети..."):
                search_res = search.run(f"site:consultant.ru OR site:pravo.gov.ru {user_input}")
                st.write(search_res)

        with col2:
            st.subheader("⚖️ 2. Юрист")
            with st.spinner("Анализирую..."):
                legal_analysis = llm.invoke(f"Проанализируй ситуацию: {user_input}\nДанные из сети: {search_res}").content
                st.write(legal_analysis)

        with col3:
            st.subheader("📝 3. Составитель иска")
            with st.spinner("Составляю документ..."):
                doc = llm.invoke(f"Составь проект иска на основе анализа: {legal_analysis}").content
                st.write(doc)
else:
    st.info("Введите API key в левом меню для старта.")
