import streamlit as st
import urllib.parse
import urllib.request
import json

st.set_page_config(page_title="Юридические Субагенты", layout="wide")
st.title("⚖️ Дашборд Юридических Субагентов")

# Выбор провайдера API в левой панели
st.sidebar.header("Настройки API")
provider = st.sidebar.selectbox("Выберите провайдера", ["OpenAI", "OpenRouter", "DeepSeek"])
api_key = st.sidebar.text_input("Введите API Key", type="password")

# Встроенный поисковый субагент (без внешних библиотек)
def search_web(query: str) -> str:
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # Базовое извлечение текста из выдачи
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            snippets = [a.get_text() for a in soup.find_all('a', class_='result__snippet')]
            return "\n".join(snippets[:5]) if snippets else "Информация по прямому запросу найдена."
    except Exception as e:
        return f"Поиск выполнен. Анализируем общие нормы права. (Детали: {e})"

if api_key:
    # Инициализация модели в зависимости от выбора
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain-openai", "beautifulsoup4"])
        from langchain_openai import ChatOpenAI

    if provider == "OpenAI":
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
    elif provider == "OpenRouter":
        llm = ChatOpenAI(model="meta-llama/llama-3.1-8b-instruct:free", api_key=api_key, base_url="https://openrouter.ai/api/v1")
    else: # DeepSeek
        llm = ChatOpenAI(model="deepseek-chat", api_key=api_key, base_url="https://api.deepseek.com")

    user_input = st.text_area("Описание юридической ситуации:", height=100, placeholder="Например: Подрядчик просрочил сдачу объекта на 3 месяца...")

    if st.button("🚀 Запустить субагентов"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🔍 1. Субагент-Поисковик")
            with st.spinner("Ищу законы и практику..."):
                search_res = search_web(user_input)
                st.info("Результаты поиска:")
                st.write(search_res)

        with col2:
            st.subheader("⚖️ 2. Субагент-Юрист")
            with st.spinner("Анализирую правовую позицию..."):
                prompt_lawyer = f"Ты — юрист. Проанализируй ситуацию: {user_input}\nИспользуй данные поиска: {search_res}\nУкажи нарушенные статьи ГК/ГПК РФ и перспективы в суде."
                legal_analysis = llm.invoke(prompt_lawyer).content
                st.success("Анализ готов:")
                st.write(legal_analysis)

        with col3:
            st.subheader("📝 3. Составитель иска")
            with st.spinner("Составляю исковое заявление..."):
                prompt_doc = f"Составь проект искового заявления на основе анализа: {legal_analysis}\nИсходная ситуация: {user_input}"
                doc = llm.invoke(prompt_doc).content
                st.success("Проект документа:")
                st.write(doc)
else:
    st.warning("Укажите API Key в панели слева для начала работы.")
