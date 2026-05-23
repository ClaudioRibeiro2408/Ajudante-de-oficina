import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime

# Configuração premium da página
st.set_page_config(
    page_title="Oficina Inteligente - Gestão Total", 
    page_icon="🚀",
    layout="centered"
)

# Nome do arquivo de banco de dados
ARQUIVO_BANCO = "historico_os.json"

# Funções de Banco de Dados
def carregar_historico():
    if os.path.exists(ARQUIVO_BANCO):
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def salvar_no_historico(cliente, veiculo, placa, tipo, relato, resultado):
    historico = carregar_historico()
    nova_entrada = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cliente": cliente,
        "veiculo": veiculo,
        "placa": placa.upper().strip(),
        "tipo": tipo,
        "relato": relato,
        "resultado": resultado
    }
    historico.append(nova_entrada)
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

# Título Principal
st.title("🚀 Oficina Inteligente")
st.write("---")

# Definição das 3 Abas
aba_patio, aba_orcamento, aba_historico = st.tabs([
    "🔧 Diagnóstico Técnico", 
    "💰 Gerar Orçamento", 
    "🗂️ Histórico de Veículos"
])

# Chave da API
api_key = os.environ.get("GEMINI_API_KEY")

# Função de IA Multimodal
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
    else:
        return f"Erro na API (Status {response.status_code})"

# ==========================================
# ABA 1: DIAGNÓSTICO E ENGENHARIA
# ==========================================
with aba_patio:
    st.subheader("🔧 Diagnóstico de Alta Performance")
    c1, c2, c3 = st.columns([2, 2, 1])
    cli_p = c1.text_input("Cliente:", key="cli_p")
    veh_p = c2.text_input("Veículo:", key="veh_p")
    plc_p = c3.text_input("Placa:", key="plc_p").upper()

    prompt_p = st.text_area("Descreva o sintoma ou peça o esquema elétrico/ajuste de osciloscópio:")
    midia_p = st.file_uploader("Envie Foto/Vídeo/Áudio do defeito:", type=["png","jpg","jpeg","mp4","mov","avi","mp3","wav","m4a"])

    if st.button("Executar Análise de Engenharia", use_container_width=True):
        if not api_key:
            st.error("API Key ausente.")
        else:
            with st.spinner("🚀 Consultando Engenharia de Fábrica..."):
                diretriz = "Você é Engenheiro-Chefe. Dê diagnóstico, esquema elétrico e parametrização de osciloscópio (Tempo/Tensão/Conexão). Títulos: ### 📋 Dados, ### ⚡ Análise, ### 🛠️ Elétrica, ### 🔬 Osciloscópio, ### 💡 Diagnóstico."
                res = chamar_gemini(f"{diretriz}\nCarro:{veh_p}\nRelato:{prompt_p}", midia_p)
                st.markdown(res)
                if plc_p:
                    salvar_no_historico(cli_p, veh_p, plc_p, "🔧 Diagnóstico", prompt_p, res)

# ==========================================
# ABA 2: ORÇAMENTO COMERCIAL PRO
# ==========================================
with aba_orcamento:
    st.subheader("💰 Gerador de Orçamento Premium")
    c1, c2, c3 = st.columns([2, 2, 1])
    cli_o = c1.text_input("Cliente:", key="cli_o")
    veh_o = c2.text_input("Veículo:", key="veh_o")
    plc_o = c3.text_input("Placa:", key="plc_o").upper()

    st.write("---")
    lista_pecas = st.text_area("Liste as peças e valores (Ex: 4 Velas - 200,00 | Kit Correia - 450,00):")
    mao_obra = st.number_input("Valor da Mão de Obra (R$):", min_value=0.0, step=50.0)
    
    if st.button("Gerar Orçamento para WhatsApp", use_container_width=True):
        if not api_key:
            st.error
