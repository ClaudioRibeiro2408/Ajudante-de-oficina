import streamlit as st
import json
import os
import pandas as pd
import requests

st.set_page_config(page_title="Oficina Pro", layout="wide")

def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "ERRO: Chave API não encontrada no Secrets."
    
    # URL corrigida para o endpoint oficial atual
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # Aqui vamos capturar o erro real do Google para sabermos se o problema é o modelo
            return f"ERRO API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"ERRO DE CONEXÃO: {str(e)}"

st.title("⚙️ Oficina Pro")

aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "📦 Estoque", "🔧 Diagnóstico", "📋 Histórico"])

with aba3:
    st.header("Diagnóstico Técnico")
    veiculo = st.text_input("Veículo")
    problema = st.text_area("Sintoma")
    
    if st.button("Buscar"):
        if veiculo and problema:
            with st.spinner("Consultando IA..."):
                prompt = f"O veículo é {veiculo} e apresenta: {problema}. Liste 3 causas e testes."
                resultado = chamar_gemini(prompt)
                
                # Exibição segura
                st.markdown("### Resultado:")
                st.write(resultado)
        else:
            st.warning("Preencha tudo.")
