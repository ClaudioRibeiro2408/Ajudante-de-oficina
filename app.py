import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from fpdf import FPDF
from PIL import Image
import io

# Configuração premium da página
st.set_page_config(
    page_title="Oficina Inteligente - Gestão Total", 
    page_icon="🚀",
    layout="centered"
)

# Nomes dos arquivos de banco de dados
ARQUIVO_BANCO = "historico_os.json"
ARQUIVO_CLIENTES = "clientes_veiculos.json"

# Inicializa a lista de itens do orçamento na memória do navegador
if "itens_orcamento" not in st.session_state:
    st.session_state.itens_orcamento = []

# ==========================================
# FUNÇÕES DE BANCO DE DADOS (JSON)
# ==========================================
def carregar_historico():
    if os.path.exists(ARQUIVO_BANCO):
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_no_historico(cliente, veiculo, placa, tipo, relato, resultado, status="N/A"):
    historico = carregar_historico()
    nova_entrada = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cliente": cliente,
        "veiculo": veiculo,
        "placa": placa.upper().strip(),
        "tipo": tipo,
        "relato": relato,
        "resultado": resultado,
        "status": status
    }
    historico.append(nova_entrada)
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

def carregar_clientes():
    if os.path.exists(ARQUIVO_CLIENTES):
        with open(ARQUIVO_CLIENTES, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def salvar_cliente(nome, telefone, placa, marca, modelo, ano, motorizacao):
    clientes = carregar_clientes()
    clientes = [c for c in clientes if c["placa"] != placa.upper().strip()]
    
    novo_cadastro = {
        "nome": nome.strip(),
        "telefone": telefone.strip(),
        "placa": placa.upper().strip(),
        "marca": marca.strip(),
        "modelo": modelo.strip(),
        "ano": ano.strip(),
        "motorizacao": motorizacao.strip()
    }
    clientes.append(novo_cadastro)
    with open(ARQUIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)

# ==========================================
# FUNÇÃO GERADORA DE PDF COM SUPORTE A LOGO
# ==========================================
def generar_pdf_orcamento(dados_oficina, cliente, veiculo, placa, reclamacao, itens, total, bytes_logo=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Se o usuário carregou uma logo na tela, insere ela no PDF
    if bytes_logo is not None:
        try:
            # Salva temporariamente os bytes para o FPDF conseguir ler
