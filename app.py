import streamlit as st
import json
import os
import pandas as pd
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Configuração da Página
st.set_page_config(page_title="Oficina Pro - Gestão & IA", layout="wide")

# --- FUNÇÕES ---
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# --- INTERFACE ---
st.title("⚙️ Oficina Pro | Gestão e Diagnóstico IA")
aba1, aba2, aba3, aba4 = st.tabs(["👤 Clientes", "💰 Orçamento", "🔧 Diagnóstico", "📋 Histórico"])

# ABA 1: CLIENTES CORRIGIDA
with aba1:
    st.header("👤 Cadastro de Clientes")
    with st.form("form_cli", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Cliente")
            telefone = st.text_input("Telefone")
        with c2:
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            motor = st.text_input("Motorização")
        
        btn_c = st.form_submit_button("Salvar Cliente")
        if btn_c:
            if nome:
                dados = carregar_json("clientes.json")
                dados.append({"Nome": nome, "Telefone": telefone, "Marca": marca, "Modelo": modelo, "Motor": motor})
                salvar_json("clientes.json", dados)
                st.success("Cliente salvo com sucesso!")
                st.rerun()
            else:
                st.error("O Nome é obrigatório.")

    # Exibição segura da tabela
    dados_cli = carregar_json("clientes.json")
    if dados_cli:
        st.table(pd.DataFrame(dados_cli))
    else:
        st.info("Nenhum cliente cadastrado.")

# ABA 2: ORÇAMENTO (MANTIDA)
with aba2:
    st.header("💰 Orçamento Técnico")
    # ... (seu código da aba 2 que já estava funcionando) ...
    st.write("Configuração de orçamento ativa.")

# (Restante do código...)
