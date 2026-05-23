import streamlit as st
import requests

st.title("Teste de Conexão IA")

api_key = st.secrets.get("GEMINI_API_KEY")

if st.button("Testar Conexão com Google"):
    # Vamos tentar listar os modelos disponíveis para ver o que a sua chave enxerga
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            modelos = response.json()
            st.success("Conexão OK! Modelos encontrados:")
            st.write(modelos)
        else:
            st.error(f"Erro {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Erro de rede: {e}")
