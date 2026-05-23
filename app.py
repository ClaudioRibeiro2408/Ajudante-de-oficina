import streamlit as st
import json
import os
import pandas as pd
import requests

# Configuração de Layout
st.set_page_config(page_title="Oficina Pro", layout="wide")

def chamar_gemini(prompt):
    # Recupera a chave do Secrets
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "Erro: Chave não encontrada no Secrets."
    
    # URL padrão e modelo clássico (gemini-pro) que funciona em todas as chaves
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na API ({response.status_code}): O Google rejeitou a chave ou modelo."
    except Exception as e:
        return f"Erro técnico: {str(e)}"

# Interface Principal
st.title("⚙️ Oficina Pro")
tabs = st.tabs(["👤 Clientes", "📦 Estoque", "🔧 Diagnóstico", "📋 Histórico"])

# ABA DIAGNÓSTICO (A que importa agora)
with tabs[2]:
    st.header("Diagnóstico Técnico IA")
    veiculo = st.text_input("Veículo")
    problema = st.text_area("Descreva o sintoma")
    
    if st.button("Buscar Diagnóstico"):
        if veiculo and problema:
            with st.spinner("Analisando..."):
                prompt = f"Como mecânico, analise este problema: {veiculo} com {problema}. Liste 3 causas e testes."
                resultado = chamar_gemini(prompt)
                st.write(resultado)
        else:
            st.error("Preencha o veículo e o sintoma.")
