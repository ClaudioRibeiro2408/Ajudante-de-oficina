import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Oficina Pro", layout="wide")

# Inicialização direta - Sem busca automática para evitar erros de atributos
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Usando a versão correta do nome do modelo
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro na conexão: {e}")
    st.stop()
