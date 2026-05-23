import streamlit as st
import json
import os
import pandas as pd
import requests

# Configuração da Página
st.set_page_config(page_title="Oficina Pro - Gestão & IA", layout="wide")

# --- FUNÇÕES DE APOIO ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "Erro: Chave API não configurada nos Secrets do Streamlit."
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- INTERFACE ---
st.title("⚙️ Oficina Pro | Gestão e Diagnóstico IA")

aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "📦 Estoque", "🔧 Diagnóstico Técnico", "📋 Histórico"])

# ABA 1: CLIENTES
with aba1:
    st.header("Cadastro de Clientes")
    with st.form("form_cli"):
        nome = st.text_input("Nome do Cliente")
        placa = st.text_input("Placa do Veículo")
        if st.form_submit_button("Salvar Cliente"):
            dados = carregar_json("clientes.json")
            dados.append({"Nome": nome, "Placa": placa})
            salvar_json("clientes.json", dados)
            st.success("Salvo!")
    st.table(pd.DataFrame(carregar_json("clientes.json")))

# ABA 2: ESTOQUE
with aba2:
    st.header("Almoxarifado")
    with st.form("form_estoque"):
        item = st.text_input("Nome da Peça")
        preco = st.number_input("Preço R$", value=0.0)
        if st.form_submit_button("Salvar Peça"):
            dados = carregar_json("estoque.json")
            dados.append({"Peça": item, "Preço": preco})
            salvar_json("estoque.json", dados)
            st.rerun()
    st.table(pd.DataFrame(carregar_json("estoque.json")))

# ABA 3: DIAGNÓSTICO COM IA
with aba3:
    st.header("🔧 Diagnóstico Técnico Inteligente")
    veiculo = st.text_input("Veículo/Modelo")
    problema = st.text_area("Descreva o sintoma ou falha")
    
    if st.button("Buscar Diagnóstico IA"):
        if veiculo and problema:
            with st.spinner("Consultando base de conhecimento técnico..."):
                prompt = f"O mecânico está diagnosticando um {veiculo}. O problema relatado é: {problema}. Liste as 3 causas mais prováveis e os procedimentos de teste sugeridos de forma técnica e objetiva."
                resultado = chamar_gemini(prompt)
                st.markdown("### 💡 Resultado da Análise:")
                st.write(resultado)
        else:
            st.error("Preencha o veículo e o problema para a IA analisar.")

# ABA 4: HISTÓRICO
with aba4:
    st.header("📋 Histórico Geral")
    st.info("Aqui ficam registradas as manutenções anteriores.")
