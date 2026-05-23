import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# ==========================================
# 1. CONFIGURAÇÃO E ESTILO (O DESIGN)
# ==========================================
st.set_page_config(
    page_title="Oficina Inteligente Pro", 
    page_icon="⚙️",
    layout="wide" # Mudamos para Wide para dar mais espaço
)

# Injeção de CSS para um visual Premium
st.markdown("""
    <style>
    /* Fundo principal e fontes */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161b22;
        padding: 10px 20px;
        border-radius: 15px 15px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #21262d;
        border-radius: 8px;
        color: #8b949e;
        border: none;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: white !important;
        font-weight: bold;
    }

    /* Estilização de Botões */
    div.stButton > button:first-child {
        background-color: #238636;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #2ea043;
        transform: scale(1.02);
    }

    /* Cards de Informação */
    .css-1r6slb0, .st-emotion-cache-1r6slb0 {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Estilo para Títulos */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #0d1117 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNÇÕES DE BANCO DE DADOS
# ==========================================
ARQUIVO_BANCO = "historico_os.json"
ARQUIVO_CLIENTES = "clientes_veiculos.json"
ARQUIVO_CATALOGO = "catalogo_itens.json"
ARQUIVO_CONFIG = "config_oficina.json"

if "itens_orcamento" not in st.session_state:
    st.session_state.itens_orcamento = []

def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return [] if "config" not in arquivo else {}
    return [] if "config" not in arquivo else {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. BARRA LATERAL (IDENTIDADE)
# ==========================================
config_salva = carregar_json(ARQUIVO_CONFIG)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1085/1085813.png", width=80) # Ícone pro
    st.markdown("### ⚙️ Painel de Controle")
    oficina_nome = st.text_input("Oficina:", value=config_salva.get("nome", "Ribeiro & Claudio Automotiva"))
    oficina_end = st.text_input("Endereço:", value=config_salva.get("endereco", "Rua Principal, 123"))
    oficina_tel = st.text_input("WhatsApp:", value=config_salva.get("telefone", "(45) 99999-9999"))
    if st.button("💾 Gravar Dados"):
        salvar_json(ARQUIVO_CONFIG, {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel})
        st.success("Dados Gravados!")
    st.write("---")
    st.caption("v2.0 PRO | Sistema Blindado")

dados_oficina = {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel}

# ==========================================
# 4. INTERFACE PRINCIPAL
# ==========================================
st.markdown(f"# 🚀 {oficina_nome}")
st.write("---")

aba_patio, aba_orcamento, aba_clientes, aba_catalogo, aba_historico = st.tabs([
    "🔧 Diagnóstico Técnico", 
    "💰 Gerador de Orçamentos",
    "🗂️ Clientes & Veículos",
    "📦 Almoxarifado",
    "📊 Histórico Geral"
])

api_key = os.environ.get("GEMINI_API_KEY")

def chamar_gemini(contexto_prompt, midia=None):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
    parts = []
    if midia:
        bytes_arquivo = midia.read()
        base64_arquivo = base64.b64encode(bytes_arquivo).decode('utf-8')
        parts.append({"inlineData": {"mimeType": midia.type, "data": base64_arquivo}})
        midia.seek(0)
    parts.append({"text": contexto_prompt})
    payload = {"contents": [{"parts": parts}]}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200: return response.json()['candidates'][0]['content']['parts'][0]['text']
    else: return "Erro na API."

# ==========================================
# CONTEÚDO DAS ABAS (RESUMIDO PARA ESTILO)
# ==========================================

# ABA: ORÇAMENTO (Onde o design mais brilha)
with aba_orcamento:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🚗 Seleção de Veículo")
        lista_cadastrados = carregar_json(ARQUIVO_CLIENTES)
        opcoes = ["Digitar Manualmente"] + [f"{c['placa']} - {c['nome']}" for c in lista_cadastrados]
        escolha = st.selectbox("Selecione o Cliente:", opcoes)
        
        reclamacao = st.text_area("📋 Queixa do Cliente:", placeholder="O que o cliente relatou?")
        status_o = st.selectbox("📊 Status:", ["Aguardando Orçamento", "Aprovado", "Executando", "Finalizado"])

    with col2:
        st.markdown("### 🖼️ Logo do Orçamento")
        arquivo_logo = st.file_uploader("Upload da Logo para o PDF:", type=["png", "jpg"])
        if arquivo_logo:
            st.image(arquivo_logo, width=150)
            logo_bytes = arquivo_logo.read()
        else:
            logo_bytes = None
            st.info("O cabeçalho do PDF usará o nome da oficina.")

    st.write("---")
    st.markdown("### 📦 Itens e Serviços")
    
    col_it1, col_it2, col_it3 = st.columns([2, 1, 1])
    catalogo = carregar_json(ARQUIVO_CATALOGO)
    
    if catalogo:
        desc_opcoes = [f"{i['descricao']} (R$ {i['preco']:.2f})" for i in catalogo]
        item_sel = col_it1.selectbox("Buscar no Almoxarifado:", desc_opcoes)
        qtd = col_it2.number_input("Quantidade:", min_value=0.1, value=1.0)
        
        if col_it3.button("➕ Adicionar"):
            item_obj = catalogo[desc_opcoes.index(item_sel)]
            st.session_state.itens_orcamento.append({
                "descricao": item_obj['descricao'],
                "quantidade": f"{qtd}",
                "valor": qtd * item_obj['preco']
            })
            st.rerun()
    else:
        st.warning("Cadastre itens no Almoxarifado primeiro!")

    # RESUMO VISUAL
    st.write("---")
    if st.session_state.itens_orcamento:
        st.markdown("### 📋 Resumo Financeiro")
        total = 0
        for idx, item in enumerate(st.session_state.itens_orcamento):
            c_a, c_b, c_c, c_d = st.columns([3, 1, 1, 0.5])
            c_a.write(f"🔹 {item['descricao']}")
            c_b.write(f"Qtd: {item['quantidade']}")
            c_c.write(f"**R$ {item['valor']:.2f}**")
            if c_d.button("❌", key=f
