import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO E DESIGN PREMIUM
# ==========================================
st.set_page_config(page_title="Oficina Pro - Command Center", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #161b22; padding: 10px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #21262d; border-radius: 8px; color: #8b949e; border: none; }
    .stTabs [aria-selected="true"] { background-color: #58a6ff !important; color: white !important; }
    div.stButton > button { background-color: #238636; color: white; border-radius: 10px; width: 100%; font-weight: bold; border: none; height: 3em; }
    .metric-card { background-color: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    h1, h2, h3 { color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ARQUIVOS DE BANCO DE DADOS
# ==========================================
ARQUIVO_BANCO = "historico_os.json"
ARQUIVO_CLIENTES = "clientes_veiculos.json"
ARQUIVO_CATALOGO = "catalogo_itens.json"
ARQUIVO_CONFIG = "config_oficina.json"

if "itens_orcamento" not in st.session_state: st.session_state.itens_orcamento = []

def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return [] if "config" not in arquivo else {}
    return [] if "config" not in arquivo else {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def atualizar_estoque_item(descricao_item, qtd_usada):
    catalogo = carregar_json(ARQUIVO_CATALOGO)
    for item in catalogo:
        if item['descricao'] == descricao_item:
            item['estoque'] = max(0, float(item.get('estoque', 0)) - float(qtd_usada))
    salvar_json(ARQUIVO_CATALOGO, catalogo)

# ==========================================
# 3. INTERFACE E ABAS
# ==========================================
config_salva = carregar_json(ARQUIVO_CONFIG)
st.markdown(f"# ⚙
