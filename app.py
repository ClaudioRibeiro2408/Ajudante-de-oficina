import streamlit as st
import json
import os
import pandas as pd

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

# Navegação
c1, c2, c3 = st.columns(3)
if c1.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
if c2.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
if c3.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"
if st.button("➕ Novo Orçamento", use_container_width=True, type="primary"): st.session_state.pagina = "Orçamento"
st.divider()

# 1. CLIENTES (Com todos os campos)
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
            d = carregar_dados("clientes.json")
            d.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Placa": placa})
            salvar_dados("clientes.json", d); st.rerun()
    st.table(pd.DataFrame(carregar_dados("clientes.json")))

# 2. ORÇAMENTO (Com os campos detalhados)
elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    cli = carregar_dados("clientes.json")
    cliente = st.selectbox("Selecione o Cliente", [""] + [c['Nome'] for c in cli])
    with st.form("orc_form", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Peça", "Serviço"], horizontal=True)
        item = st.text_input("Descrição do Item")
        detalhes = st.text_area("Detalhes (opcional)")
        c1, c2 = st.columns(2)
        unid = c1.text_input("Unidade")
        qtd = c2.number_input("Quantidade", min_value=1, value=1)
        custo = st.number_input("Custo (R$)", min_value=0.0)
        venda = st.number_input("Venda (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            d = carregar_dados("orcamentos.json")
            d.append({"Cliente": cliente, "Tipo": tipo, "Item": item, "Detalhes": detalhes, "Unid": unid, "Qtd": qtd, "Custo": custo, "Venda": venda})
            salvar_dados("orcamentos.json", d); st.rerun()
    
    lista = carregar_dados("orcamentos.json")
    if lista: st.table(pd.DataFrame([i for i in lista if i['Cliente'] == cliente]))

# 3. DIAGNÓSTICO
elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico Técnico IA")
    if st.button("Analisar"): st.write("Sistema pronto para diagnóstico.")

# 4. HISTÓRICO E FINANCEIRO
elif st.session_state.pagina == "Histórico":
    st.header("📋 Histórico Financeiro")
    orc = carregar_dados("orcamentos.json")
    if orc:
        df = pd.DataFrame(orc)
        st.metric("Total Faturado", f"R$ {df['Venda'].sum():.2f}")
        st.table(df)

if st.session_state.pagina != "Início":
    if st.button("⬅️ Voltar"): st.session_state.pagina = "Início"; st.rerun()
