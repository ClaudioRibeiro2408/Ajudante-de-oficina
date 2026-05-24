import streamlit as st
import json
import os
import pandas as pd
import requests

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
    st.session_state.pagina = "Orçamento" # Começa direto na principal

# --- MENU PRINCIPAL (Layout Ajustado) ---
# Botões alinhados
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👤 Clientes", use_container_width=True): st.session_state.pagina = "Clientes"
with col2:
    if st.button("🔧 Diagnóstico", use_container_width=True): st.session_state.pagina = "Diagnóstico"
with col3:
    if st.button("📋 Histórico", use_container_width=True): st.session_state.pagina = "Histórico"

# Botão grande embaixo
if st.button("➕ Criar novo orçamento", use_container_width=True, type="primary"):
    st.session_state.pagina = "Orçamento"

st.divider()

# --- LÓGICA DE NAVEGAÇÃO ---
if st.session_state.pagina == "Clientes":
    st.header("👤 Clientes")
    # Aqui vamos reintegrar seu formulário de clientes
    
elif st.session_state.pagina == "Orçamento":
    st.header("💰 Novo Orçamento")
    # Aqui vamos reintegrar sua lógica de orçamentos
    
elif st.session_state.pagina == "Diagnóstico":
    st.header("🔧 Diagnóstico IA")
    # Aqui entra sua IA
    
elif st.session_state.pagina == "Histórico":
    st.header("📋 Histórico e Financeiro")
    # Aqui entra o histórico
