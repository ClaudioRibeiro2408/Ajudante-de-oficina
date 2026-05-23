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
    pdf.cell(0, 6, f"Telefone: {dados_oficina['telefone']}", ln=True, align="C")
    pdf.ln(10)
    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Dados do Atendimento
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "DADOS DO ATENDIMENTO / ORÇAMENTO", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Cliente: {cliente}", ln=False)
    pdf.cell(95, 6, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(95, 6, f"Veículo: {veiculo}", ln=False)
    pdf.cell(95, 6, f"Placa: {placa.upper()}", ln=True)
    pdf.ln(4)
    
    # Reclamação
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Reclamação Relatada pelo Cliente:", ln=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, reclamacao if reclamacao else "Não informada.")
    pdf.ln(6)
    
    # Tabela
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

# Título Principal do Painel
st.title("🚀 Oficina Inteligente")
st.write("---")

# CONFIGURAÇÕES DE IDENTIDADE NA BARRA LATERAL (SIDEBAR)
st.sidebar.markdown("### 🏢 Identidade da Oficina")
oficina_nome = st.sidebar.text_input("Nome da Oficina:", value="Ribeiro & Claudio Automotiva")
oficina_end = st.sidebar.text_input("Endereço:", value="Rua Principal, 123")
oficina_tel = st.sidebar.text_input("Telefone/WhatsApp:", value="(45) 99999-9999")
dados_oficina = {"nome": oficina_nome, "endereco": oficina_end, "telefone": oficina_tel}

# Definição das 4 Abas do Sistema
aba_patio, aba_orcamento, aba_clientes, aba_historico = st.tabs([
    "🔧 Diagnóstico Técnico", 
    "💰 Gerar Orçamento",
    "🗂️ Clientes & Carros",
    "📊 Histórico & Status"
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
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else: return f"Erro na API (Status {response.status_code})"

# ==========================================
# ABA 1: DIAGNÓSTICO E ENGENHARIA
# ==========================================
with aba_patio:
    st.subheader("🔧 Diagnóstico de Alta Performance")
    
    lista_cadastrados = carregar_clientes()
    modo_p = st.radio("Identificação do Veículo no Pátio:", ["Buscar Cliente Cadastrado", "Digitar Manualmente"], horizontal=True, key="modo_p")
    
    cli_p, veh_p, plc_p = "", "", ""
    
    if modo_p == "Buscar Cliente Cadastrado" and lista_cadastrados:
        opcoes_placa = [f"{c['placa']} - {c['nome']} ({c['modelo']})" for c in lista_cadastrados]
        selecionado = st.selectbox("Selecione o Veículo:", opcoes_placa, key="sel_p")
        idx = opcoes_placa.index(selecionado)
        dados_c = lista_cadastrados[idx]
        cli_p = dados_c["nome"]
        veh_p = f"{dados_c['marca']} {dados_c['modelo']} {dados_c['motorizacao']} {dados_c['ano']}"
        plc_p = dados_c["placa"]
        st.info(f"🚗 **Selecionado:** {veh_p} | **Cliente:** {cli_p}")
    else:
        if modo_p == "Buscar Cliente Cadastrado":
            st.warning("Nenhum cliente cadastrado ainda. Digite manualmente abaixo.")
        c1, c2, c3 = st.columns([2, 2, 1])
        cli_p = c1.text_input("Cliente:", key="cli_p_man")
        veh_p = c2.text_input("Veículo (Marca/Mod/Motor):", key="veh_p_man")
        plc_p = c3.text_input("Placa:", key="plc_p_man").upper()

    st.write("---")
    prompt_p = st.text_area("Descreva o sintoma ou peça o esquema elétrico/ajuste de osciloscópio:")
    midia_p = st.file_uploader("Envie Foto/Vídeo/Áudio do defeito:", type=["png","jpg","jpeg","mp4","mov","avi","mp3","wav","m4a"])

    if st.button("Executar Análise de Engenharia", use_container_width=True):
        if not api_key: st.error("API Key ausente.")
        else:
            with st.spinner("🚀 Consultando Engenharia..."):
                diretriz = "Você é Engenheiro-Chefe especialista. Dê diagnóstico técnico, esquema elétrico e parametrização de osciloscópio."
                res = chamar_gemini(f"{diretriz}\nCarro:{veh_p}\nRelato:{prompt_p}", midia_p)
                st.markdown(res)
                if plc_p: salvar_no_historico(cli_p, veh_p, plc_p, "🔧 Diagnóstico", prompt_p, res)

# ==========================================
# ABA 2: ORÇAMENTO COMERCIAL E DESIGN HARMONIOSO
# ==========================================
with aba_orcamento:
    # DESIGN DA LOGO / BANNER INTEGRADO
    if os.path.exists("logo.png"):
        # Se você subir uma imagem chamada logo.png no seu GitHub, ela centraliza perfeitamente aqui
        st.image("logo.png", use_container_width=True)
    else:
        # Se não houver arquivo físico de imagem, gera um layout de cabeçalho moderno e limpo via código
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e1e2f 0%, #0e0e1a 100%); 
                    padding: 25px; 
                    border-radius: 12px; 
                    text-align: center; 
                    border-left: 6px solid #ff4b4b;
                    margin-bottom: 25px;
                    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
            <h1 style="color: #ffffff; margin: 0; font-family: 'Helvetica', sans-serif; letter-spacing: 2px; font-size: 26px;">
                ⚙️ {oficina_nome.upper()}
            </h1>
            <p style="color: #a3a3c2; margin: 5px 0 0
