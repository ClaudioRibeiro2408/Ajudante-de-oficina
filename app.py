import streamlit as st
import google.generativeai as genai
import os

st.title("⚙️ Oficina Pro")

# Força a configuração da API sem usar v1beta
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Definindo o modelo de forma explícita com o prefixo 'models/'
model = genai.GenerativeModel('models/gemini-1.5-flash')

dtc = st.text_input("DTC:")
veiculo = st.text_input("Veículo:")

if st.button("Consultar"):
    try:
        response = model.generate_content(f"Analise o {veiculo} com código {dtc}.")
        st.write(response.text)
    except Exception as e:
        st.error(f"Erro: {e}")
