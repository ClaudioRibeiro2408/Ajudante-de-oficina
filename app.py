import streamlit as st
import pandas as pd
import json
import os

# Configuração Base
st.set_page_config(page_title="Oficina Pro", layout="wide")

# Estilização limpa (evita conflitos de CSS)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    h1 { color: #1e293b; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Funções de Dados Simplificadas
def carregar(arq):
    if os.path.exists(arq):
        with open(arq, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar(arq, dados):
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Título
st.title("⚙️ Oficina Pro | Gestão Simplificada")

# Colunas principais para organizar a tela
col_form, col_lista = st.columns([1, 2])

with col_form:
    st.subheader("➕ Novo Cliente")
    nome = st.text_input("Nome do Cliente")
    placa = st.text_input("Placa do Veículo")
    if st.button("💾 Adicionar Cliente"):
        if nome and placa:
            dados = carregar("clientes.json")
            dados.append({"Nome": nome, "Placa": placa.upper()})
            salvar("clientes.json", dados)
            st.rerun()

with col_lista:
    st.subheader("📋 Clientes Cadastrados")
    dados = carregar("clientes.json")
    if dados:
        st.dataframe(pd.DataFrame(dados), use_container_width=True)
    else:
        st.info("Nenhum cliente cadastrado.")

st.divider()

# Área de Estoque
st.subheader("📦 Estoque de Peças")
col_est1, col_est2 = st.columns([1, 3])
with col_est1:
    peca = st.text_input("Peça")
    preco = st.number_input("Preço R$", value=0.0)
    if st.button("➕ Cadastrar Peça"):
        dados = carregar("estoque.json")
        dados.append({"Peça": peca, "Preço": preco})
        salvar("estoque.json", dados)
        st.rerun()

with col_est2:
    dados_est = carregar("estoque.json")
    if dados_est:
        st.dataframe(pd.DataFrame(dados_est), use_container_width=True)
