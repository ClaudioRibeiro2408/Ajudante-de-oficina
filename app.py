import streamlit as st
import requests
import json

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro - Modo Conexão Direta")

api_key = st.secrets["GOOGLE_API_KEY"]
dtc = st.text_input("DTC:")
veiculo = st.text_input("Veículo:")
btn = st.button("Consultar")

if btn:
    # URL da API v1 (estável)
    # Altere a variável 'url' para usar gemini-1.0-pro
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"Atue como mecânico. Analise o {veiculo} com erro {dtc}. Forneça causas, esquema e dicas de osciloscópio."}]
        }]
    }
    
    try:
        with st.spinner("Consultando servidor..."):
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if "candidates" in result:
                texto = result["candidates"][0]["content"]["parts"][0]["text"]
                st.markdown(texto)
            else:
                st.error(f"Erro do Servidor: {result}")
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
