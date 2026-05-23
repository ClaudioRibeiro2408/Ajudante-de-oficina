import streamlit as st
import pandas as pd
import json
import os

# Configuração de Layout
st.set_page_config(page_title="Oficina Pro - Command Center", page_icon="⚙️", layout="wide")

# Estilo Premium
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .metric-card { background-color: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; text-align: center; }
    h1, h2, h3 { color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# Arquivos
ARQUIVO_CLIENTES = "clientes_veiculos.json"
ARQUIVO_CATALOGO = "catalogo_itens.json"
ARQUIVO_BANCO = "historico_os.json"

# Funções de Banco
def carregar(arq):
    if os.path.exists(arq):
        with open(arq, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar(arq, dados):
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Título
st.markdown("# ⚙️ Central de Comando Oficina Pro")

# Abas
aba1, aba2, aba3, aba4 = st.tabs(["👥 Clientes", "📦 Estoque", "💰 Orçamentos", "📊 Dashboard"])

# 1. ABA CLIENTES (O seu pedido)
with aba1:
    st.subheader("👤 Cadastro de Clientes e Veículos")
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Cliente")
        placa = col2.text_input("Placa do Veículo")
        if st.form_submit_button("💾 Salvar Cliente"):
            dados = carregar(ARQUIVO_CLIENTES)
            dados.append({"Nome": nome, "Placa": placa})
            salvar(ARQUIVO_CLIENTES, dados)
            st.success("Cliente cadastrado!")
    
    st.dataframe(pd.DataFrame(carregar(ARQUIVO_CLIENTES)), use_container_width=True)

# 2. ABA ESTOQUE
with aba2:
    st.subheader("📦 Gestão de Estoque")
    with st.form("add_peca"):
        c1, c2, c3 = st.columns(3)
        nome_p = c1.text_input("Nome da Peça")
        preco_p = c2.number_input("Preço R$", value=0.0)
        qtd_p = c3.number_input("Qtd Inicial", value=1)
        if st.form_submit_button("Cadastrar Peça"):
            cat = carregar(ARQUIVO_CATALOGO)
            cat.append({"descricao": nome_p, "preco": preco_p, "estoque": qtd_p})
            salvar(ARQUIVO_CATALOGO, cat)
            st.rerun()
    st.dataframe(pd.DataFrame(carregar(ARQUIVO_CATALOGO)), use_container_width=True)

# 3. ABA ORÇAMENTOS
with aba3:
    st.subheader("💰 Gerador de Orçamentos")
    st.info("Selecione peças do estoque para compor seu orçamento.")
    # (Aqui entra sua lógica de montar orçamento...)

# 4. ABA DASHBOARD
with aba4:
    st.subheader("📊 Painel de Performance")
    # (Aqui entra o gráfico de faturamento...)
