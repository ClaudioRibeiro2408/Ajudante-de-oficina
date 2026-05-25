import streamlit as st
import google.generativeai as genai
import os

# Força a limpeza de qualquer configuração anterior
os.environ["GOOGLE_API_VERSION"] = "v1"

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usamos o nome do modelo sem prefixos, para evitar conflitos de versão
model = genai.GenerativeModel('gemini-1.5-flash')
