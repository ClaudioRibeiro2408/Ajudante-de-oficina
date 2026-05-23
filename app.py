import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime

# Configuração premium da página
st.set_page_config(
    page_title="Oficina Inteligente - Diagnóstico Avançado", 
    page_icon="🚀",
    layout="centered"
)

# Nome do arquivo que funcionará como banco de dados
ARQUIVO_BANCO = "historico_os.json"

# Funções para gerenciar o banco de dados JSON
def carregar_historico():
    if os.path.exists(ARQUIVO_BANCO):
        with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def salvar_no_historico(cliente, veiculo, placa, tipo_laudo, relato, resultado):
    historico = carregar_historico()
    nova_os = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cliente": cliente,
        "veiculo": veiculo,
        "placa": placa.upper().strip(),
        "tipo": tipo_laudo,
        "relato": relato,
        "resultado": resultado
    }
    historico.append(nova_os)
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

# Título Principal do App
st.title("🚀 Oficina Inteligente")
st.write("---")

# Criação de Abas: Uma para trabalhar no pátio e outra para consultar o histórico
aba_patio, aba_historico = st.tabs(["🔧 Nova Ordem de Serviço", "🗂️ Histórico de Diagnósticos"])

# Resgata a chave da API
api_key = os.environ.get("GEMINI_API_KEY")

# ==========================================
# ABA 1: TRABALHO DE PÁTIO (NOVA O.S.)
# ==========================================
with aba_patio:
    st.subheader("Abertura de Diagnóstico / O.S.")
    
    # Linha com os dados de identificação do veículo
    col_cli, col_veh, col_plc = st.columns([2, 2, 1])
    with col_cli:
        nome_cliente = st.text_input("👤 Nome do Cliente:", placeholder="Ex: João Silva")
    with col_veh:
        modelo_veiculo = st.text_input("🚗 Veículo / Motorização:", placeholder="Ex: Golf 1.4 TSI 2016")
    with col_plc:
        placa_veiculo = st.text_input("🔢 Placa:", placeholder="ABC-1234").upper().strip()

    st.write("---")

    # Área de Entrada de Dados do Pátio
    prompt = st.text_area(
        "📝 Relato Técnico / Sintomas ou Solicitação de Esquema Elétrico:", 
        placeholder="Descreva o defeito ou solicite o esquema elétrico e parametrização do osciloscópio aqui...",
        height=120
    )

    # Campo para Envio de Arquivos (Fotos, Vídeos ou Áudios)
    arquivo_enviado = st.file_uploader(
        "📸 Insira as mídias do pátio (Foto do Scanner, Gráfico do Osciloscópio, etc.):", 
        type=["png", "jpg", "jpeg", "mp4", "mov", "avi", "mp3", "wav", "m4a", "ogg"]
    )

    if arquivo_enviado is not None:
        if arquivo_enviado.type.startswith('image'):
            st.image(arquivo_enviado, caption="Análise Visual Ativada 🔍", use_container_width=True)
        elif arquivo_enviado.type.startswith('video'):
            st.video(arquivo_enviado)
        elif arquivo_enviado.type.startswith('audio'):
            st.audio(arquivo_enviado)

    st.write("---")
    st.write("### 🎛️ Central de Comando")

    col1, col2 = st.columns(2)
    with col1:
        botao_tecnico = st.button("🔧 Diagnóstico e Esquema Elétrico", use_container_width=True)
    with col2:
        botao_cliente = st.button("💬 Traduzir para Laudo do Cliente (WhatsApp)", use_container_width=True)

    # Função de comunicação com a API do Gemini
    def chamar_gemini(contexto_prompt, midia):
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
        parts = []
        if midia is not None:
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
            return f"Erro no servidor do Google (Código {response.status_code}): {response.text}"

    # PROMPTS DE ENGENHARIA E ATENDIMENTO
    DIRETRIZ_SUPREMA_TECNICA = """Você é o Engenheiro-Chefe de Fábrica e Mestre de Diagnóstico Avançado. Forneça análises elétricas de falhas, pinagem detalhada de esquemas elétricos se solicitado, e um Guia do Osciloscópio completo (Conexão, tempo/tensão por divisão e sinal esperado). Formate estritamente com os títulos: ### 📋 Dados Técnicos Extraídos, ### ⚡ Análise Elétrica e Lógica de Falhas, ### 🛠️ Mapeamento de Esquema Elétrico & Pinagens, ### 🔬 Guia do Osciloscópio, ### 🔍 Roteiro Prático de Testes, ### 💡 Diagnóstico Provável."""
    DIRETRIZ_SUPREMA_CLIENTE = """Você é o Diretor de Atendimento de uma oficina premium. Traduza o defeito técnico em um laudo comercial transparente, amigável e profissional em tópicos com emojis para o WhatsApp do cliente. Destaque o uso de tecnologia avançada (osciloscópios/manuais de fábrica) para evitar o 'troquismo' de peças."""

    # Execução do Botão Técnico
    if botao_tecnico and (prompt or arquivo_enviado):
        if not api_key:
            st.error("Chave da API não configurada nos Segredos.")
        else:
            with st.spinner("🚀 Consultando Engenharia de Fábrica e Esquemas..."):
                contexto = f"{DIRETRIZ_SUPREMA_TECNICA}\n\nCarro: {modelo_veiculo}\nRelato: {prompt}"
                resposta = chamar_gemini(contexto,
