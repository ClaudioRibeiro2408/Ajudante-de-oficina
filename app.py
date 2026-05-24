import streamlit as st
import sys

st.set_page_config(page_title="Oficina Pro - Debug", layout="centered")

st.title("⚙️ Oficina Pro - Modo de Depuração")

st.write("Verificando ambiente...")

try:
    # Verificação simples de bibliotecas
    import google.generativeai
    st.success("✅ Biblioteca google-generativeai instalada corretamente.")
except ImportError:
    st.error("❌ Erro: Biblioteca 'google-generativeai' não instalada. Adicione ao requirements.txt!")

try:
    # Teste de Secrets sem travar o app
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("✅ Chave GOOGLE_API_KEY encontrada no Secrets.")
    else:
        st.error("❌ Erro: GOOGLE_API_KEY não encontrada no painel Secrets.")
        st.write("Dica: Vá em 'Manage App' -> 'Settings' -> 'Secrets' e cole: GOOGLE_API_KEY = 'sua_chave'")
except Exception as e:
    st.error(f"Erro inesperado ao acessar secrets: {e}")

st.divider()
st.write("Se você vê este texto, o ambiente está OK. O problema anterior era o carregamento da chave.")
