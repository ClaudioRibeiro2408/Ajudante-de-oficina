import streamlit as st
import json
import os
import pandas as pd
import requests

st.set_page_config(page_title="Oficina Pro", layout="centered")

# --- FUNÇÕES ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

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
if c1.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", type="primary", use_container_width=True): st.session_state.pagina = "Orçamento"
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
        if st.form_submit_button("Salvar"):
            d = carregar_dados("clientes.json")
            d.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Placa": placa})
            salvar_dados("clientes.json", d); st.rerun()
    st.table(pd.DataFrame(carregar_dados("clientes.json")))

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    lista_cli = carregar_dados("clientes.json")
    cliente = st.selectbox("Selecione o Cliente", [""] + [c['Nome'] for c in lista_cli])
    
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Peça", "Serviço"], horizontal=True)
        item = st.text_input("Qual é o item?")
        detalhes = st.text_area("Detalhes (opcional)")
        c1, c2 = st.columns(2)
        unidade = c1.text_input("Unidade de medida")
        qtd = c2.number_input("Quantidade", min_value=1, value=1)
        
        st.subheader("Custo & Lucro")
        c_custo, c_venda = st.columns(2)
        custo = c_custo.number_input("Custo unitário (R$)", min_value=0.0, value=0.0)
        venda = c_venda.number_input("Preço de venda final (R$)", min_value=0.0, value=0.0)
        
        if custo > 0 and venda > 0:
            margem = ((venda - custo) / venda) * 100
            st.info(f"💰 Margem de lucro atual: **{margem:.2f}%**")
        
        with st.expander("Outros detalhes"):
            marca = st.text_input("Marca")
