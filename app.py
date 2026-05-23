import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from fpdf import FPDF

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
    # Verifica se a placa já existe para não duplicar, se existir substitui os dados
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
# FUNÇÃO GERADORA DE PDF
# ==========================================
def generar_pdf_orcamento(dados_oficina, cliente, veiculo, placa, reclamacao, itens, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    
    # Cabeçalho da Oficina
    pdf.cell(0, 10, dados_oficina['nome'].upper(), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Endereço: {dados_oficina['endereco']}", ln=True, align="C")
    pdf.cell(0, 6,
