import streamlit as st
import json
import os
import pandas as pd
import requests

# Configuração da Página
st.set_page_config(page_title="Oficina Pro", layout="centered")

# --- FUNÇÕES DE APOIO ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return "Erro: Chave API não configurada."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Erro de comunicação com a IA."

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
with c2:
    if st.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
with c3:
    if st.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"

if st.button("➕ Criar novo orçamento", use_container_width=True, type="primary"): st.session_state.pagina = "Orçamento"

st.divider()

# --- PÁGINAS ---

if st.session_state.pagina == "Clientes":
    st.header("👤 Cadastro de Cliente")
    with st.form("cli_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Cliente")
        telefone = col1.text_input("Telefone")
        marca = col2.text_input("Marca do Veículo")
        modelo = col2.text_input("Modelo do Veículo")
        placa = col2.text_input("Placa")
        if st.form_submit_button("Salvar Cliente"):
            if nome:
                dados = carregar_dados("clientes.json")
                dados.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Placa": placa})
                salvar_dados("clientes.json", dados)
                st.success("Cliente salvo!")
                st.rerun()
    lista_cli = carregar_dados("clientes.json")
    if lista_cli: st.table(pd.DataFrame(lista_cli))

elif st.session_state
