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
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

# --- NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")

# Botões de Navegação
c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", use_container_width=True, type="primary"): st.session_state.pagina = "Orçamento"
st.divider()

# --- PÁGINAS ---

# 1. CLIENTES
if st.session_state.pagina == "Clientes":
    st.header("👤 Cadastro de Cliente")
    with st.form("cli_form", clear_on_submit=True):
        nome = st.text_input("Nome do Cliente")
        if st.form_submit_button("Salvar"):
            d = carregar_dados("clientes.json")
            d.append({"Nome": nome})
            salvar_dados("clientes.json", d); st.rerun()
    st.table(pd.DataFrame(carregar_dados("clientes.json")))

# 2. ORÇAMENTO (Com os campos que você pediu)
elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    cli = carregar_dados("clientes.json")
    cliente = st.selectbox("Cliente", [""] + [c['Nome'] for c in cli])
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Peça", "Serviço"], horizontal=True)
        item = st.text_input("Descrição do Item")
        detalhes = st.text_area("Detalhes (opcional)")
        c1, c2 = st.columns(2)
        unid = c1.text_input("Unidade (ex: un, kg)")
        qtd = c2.number_input("Qtd", min_value=1, value=1)
        custo = st.number_input("Custo (R$)", min_value=0.0)
        venda = st.number_input("Venda (R$)", min_value=0.0)
        
        if st.form_submit_button("Adicionar"):
            d = carregar_dados("orcamentos.json")
            d.append({"Cliente": cliente, "Tipo": tipo, "Item": item, "Venda": venda, "Qtd": qtd})
            salvar_dados("orcamentos.json", d); st.rerun()
    
    st.table(pd.DataFrame([i for i in carregar_dados("orcamentos.json") if i['Cliente'] == cliente]))

# 3. DIAGNÓSTICO
elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico Técnico")
    if st.button("Analisar"): st.write("Sistema pronto.")

# 4. HISTÓRICO
elif st.session_state.pagina == "Histórico":
    st.header("📋 Histórico Financeiro")
    orc = carregar_dados("orcamentos.json")
    if orc: st.table(pd.DataFrame(orc))

# Rodapé/Voltar
if st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"): st.session_state.pagina = "Início"; st.rerun()
