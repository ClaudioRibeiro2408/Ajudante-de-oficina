import streamlit as st
import google.generativeai as genai
import os

# Tenta pegar a chave dos secrets, se falhar, tenta pegar das variáveis de ambiente do sistema
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Erro na API: O sistema não encontrou a chave. Verifique o painel Secrets no Streamlit Cloud.")
