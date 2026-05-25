import streamlit as st
import google.generativeai as genai
import os

# FORÇANDO A API A USAR A VERSÃO ESTÁVEL V1 (O PULO DO GATO)
os.environ["GOOGLE_API_VERSION"] = "v1"

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usamos o caminho completo com 'models/' para não deixar o sistema tentar adivinhar
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
