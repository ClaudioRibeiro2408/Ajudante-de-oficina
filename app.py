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
ARQUIVO_CATALOGO = "catalogo_itens.json"
ARQUIVO_CONFIG = "config_oficina.json"

# Inicializa a lista de itens do orçamento na memória do navegador
if "itens_orcamento" not in st.session_state:
    st.session_state.itens_orcamento = []

# ==========================================
# FUNÇÕES DE BANCO DE DADOS (JSON)
# ==========================================
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return [] if "config" not in arquivo else {}
    return [] if "config" not in arquivo else {}

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def salvar_no_historico(cliente, veiculo, placa, tipo, relato, resultado, status="N/A"):
    historico = carregar_json(ARQUIVO_BANCO)
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
    salvar_json(ARQUIVO_BANCO, historico)

def salvar_cliente(nome, telefone, placa, marca, modelo, ano, motorizacao):
    clientes = carregar_json(ARQUIVO_CLIENTES)
    clientes = [c for c in clientes if c["placa"] != placa.upper().strip()]
    novo_cadastro = {
        "nome": nome.strip(), "telefone": telefone.strip(), "placa": placa.upper().strip(),
        "marca": marca.strip(), "modelo": modelo.strip(), "ano": ano.strip(), "motorizacao": motorizacao.strip()
    }
    clientes.append(novo_cadastro)
    salvar_json(ARQUIVO_CLIENTES, clientes)

def salvar_no_catalogo(tipo, descricao, preco_unitario):
    catalogo = carregar_json(ARQUIVO_CATALOGO)
    # Evita duplicados com base no nome
    catalogo = [i for i in catalogo if i["descricao"].lower() != descricao.strip().lower()]
    novo_item = {
        "tipo": tipo,
        "descricao": descricao.strip(),
        "preco": float(preco_unitario)
    }
    catalogo.append(novo_item)
    salvar_json(ARQUIVO_CATALOGO, catalogo)

# ==========================================
# FUNÇÃO GERADORA DE PDF
# ==========================================
def generar_pdf_orcamento(dados_oficina, cliente, veiculo, placa, reclamacao, itens, total, bytes_logo=None):
    pdf = FPDF()
    pdf.add_page()
    
    if bytes_logo is not None:
        try:
            img_temp = "temp_logo_pdf.png"
            image = Image.open(io.BytesIO(bytes_logo))
            image.save(img_temp)
            pdf.image(img_temp, x=85, y=10, w=40)
            pdf.ln(25)
            if os.path.exists(img_temp): os.remove(img_temp)
        except: pass
            
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, dados_oficina.get('nome', 'OFICINA').upper(), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Endereço: {dados_oficina.get('endereco', '')}", ln=True, align="C")
    pdf.cell(0, 6, f"Telefone: {dados_oficina.get('telefone', '')}", ln=True, align="C")
    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "DADOS DO ATENDIMENTO / ORÇAMENTO", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Cliente: {cliente}", ln=False)
    pdf.cell(95, 6, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(95, 6, f"Veículo: {veiculo}", ln=False)
    pdf.cell(95, 6, f"Placa: {placa.upper()}", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Reclamação Relatada pelo Cliente:", ln=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, reclamacao if reclamacao else "Não informada.")
    pdf.ln(6)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(110, 8, "Descrição do Item / Serviço", border=1, ln=False)
    pdf.cell(40, 8, "Quantidade", border=1, ln=False, align="C")
    pdf.cell(40, 8, "Total (R$)", border=1, ln=True, align="R")
    
    pdf.set_font("Helvetica", "", 10)
    for item in itens:
        pdf.cell(110, 7, item['descricao'], border=1, ln=False)
        pdf.cell(40, 7, item['quantidade'], border=1, ln=False, align="C")
        pdf.cell(40, 7, f"{item['valor']:.2f}", border=1, ln=True, align="R")
        
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(150, 8, "VALOR TOTAL DO ORÇAMENTO:", ln=False, align="R")
    pdf.cell(40, 8, f"R$ {total:.2f}", ln=True, align="R")
    
    return pdf.output()

# Título Principal
st.title("🚀 Oficina Inteligente")
st.write("---")

# CONFIGURAÇÕES DA OFICINA SALVAS EM BANCO DE DADOS
config_salva = carregar_json(ARQUIVO_CONFIG)
st.sidebar.markdown("### 🏢 Identidade da Oficina")
oficina_nome = st.sidebar.text_input("Nome da Oficina:", value=config_salva.get("nome", "Ribeiro & Claudio Automotiva"))
oficina_end = st.sidebar.text_input("Endereço:", value=config_salva.get("endereco", "Rua Principal, 123"))
oficina_tel = st.sidebar.text_input("Telefone/WhatsApp:", value=config_salva.get("telefone", "(45) 99999-9999"))

if st.sidebar.button("💾 Salvar Dados da Oficina"):
    salvar_json(ARQUIVO_CONFIG, {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel})
    st.sidebar.success("Dados da oficina gravados permanentemente!")

dados_oficina = {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel}

# Definição das 5 Abas do Sistema
aba_patio, aba_orcamento, aba_clientes, aba_catalogo, aba_historico = st.tabs([
    "🔧 Pátio & Diagnóstico", 
    "💰 Gerar Orçamento",
    "🗂️ Clientes & Veículos",
    "📦 Almoxarifado & Serviços",
    "📊 Histórico Geral"
])

api_key = os.environ.get("GEMINI_API_KEY")

def chamar_gemini(contexto_prompt, midia
