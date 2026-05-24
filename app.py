import streamlit as st
import json
import os
import pandas as pd
import requests

st.set_page_config(page_title="Oficina Pro", layout="centered")

def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f: json.dump(dados, f, ensure_ascii=False, indent=4)

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"

st.title("⚙️ Oficina Pro")

# Navegação Principal
c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes"): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico"): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico"): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", type="primary"): st.session_state.pagina = "Orçamento"
st.divider()

if st.session_state.pagina == "Clientes":
    st.header("👤 Cadastro de Cliente")
    with st.form("cli_form", clear_on_submit=True):
        nome = st.text_input("Nome")
        if st.form_submit_button("Salvar"):
            d = carregar_dados("clientes.json")
            d.append({"Nome": nome})
            salvar_dados("clientes.json", d); st.rerun()
    st.table(pd.DataFrame(carregar_dados("clientes.json")))

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    cli = carregar_dados("clientes.json")
    cliente = st.selectbox("Cliente", [""] + [c['Nome'] for c in cli])
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Peça", "Serviço"], horizontal=True)
        item = st.text_input("Descrição do Item")
        c1, c2 = st.columns(2)
        custo = c1.number_input("Custo (R$)", min_value=0.0)
        venda = c2.number_input("Venda (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            d = carregar_dados("orcamentos.json")
            d.append({"Cliente": cliente, "Tipo": tipo, "Item": item, "Venda": venda})
            salvar_dados("orcamentos.json", d); st.rerun()
    st.table(pd.DataFrame([i for i in carregar_dados("orcamentos.json") if i['Cliente'] == cliente]))

elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico IA")
    if st.button("Analisar"): st.write("Funcionalidade de IA ativa.")

elif st.session_state.pagina == "Histórico":
    st.header("📋 Histórico Financeiro")
    st.table(pd.DataFrame(carregar_dados("orcamentos.json")))

if st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar ao Início"): st.session_state.pagina = "Início"; st.rerun()
