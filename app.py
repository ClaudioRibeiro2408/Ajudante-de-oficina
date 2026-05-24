import streamlit as st
import json
import os
import pandas as pd
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Oficina Pro", layout="centered")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def carregar_dados(arquivo):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

# --- ESTADO DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

# --- INTERFACE ---
st.title("⚙️ Oficina Pro")

# Botão de Ação Principal (Estilo Agenda Boa)
if st.button("➕ Criar novo orçamento", use_container_width=True, type="primary"):
    st.session_state.pagina = "Orçamento"

# Grade de Atalhos
col1, col2 = st.columns(2)
with col1:
    if st.button("👤 Clientes", use_container_width=True):
        st.session_state.pagina = "Clientes"
    if st.button("🔧 Diagnóstico IA", use_container_width=True):
        st.session_state.pagina = "Diagnóstico"
with col2:
    if st.button("💰 Financeiro/Histórico", use_container_width=True):
        st.session_state.pagina = "Histórico"
    if st.button("🏠 Início", use_container_width=True):
        st.session_state.pagina = "Início"

st.divider()

# --- LÓGICA DE NAVEGAÇÃO ---
if st.session_state.pagina == "Clientes":
    st.header("👤 Cadastro de Clientes")
    # [Aqui entra o seu formulário de Clientes]
    if st.button("Voltar"): st.session_state.pagina = "Início"; st.rerun()

elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    # [Aqui entra a lógica de Orçamento]
    if st.button("Voltar"): st.session_state.pagina = "Início"; st.rerun()

elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico IA")
    # [Aqui entra o Diagnóstico]
    if st.button("Voltar"): st.session_state.pagina = "Início"; st.rerun()

elif st.session_state.pagina == "Histórico":
    st.header("📋 Histórico e Financeiro")
    # [Aqui entra a consulta]
    if st.button("Voltar"): st.session_state.pagina = "Início"; st.rerun()

else:
    st.info("Bem-vindo! Selecione uma opção acima para começar.")
