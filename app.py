import streamlit as st
import requests
import json
import os
import base64

# Configuração premium da página
st.set_page_config(
    page_title="Oficina Inteligente - Diagnóstico Avançado", 
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 Oficina Inteligente")
st.subheader("Central Unificada de Diagnóstico, Esquemas Elétricos e Ajustes de Osciloscópio")
st.write("---")

# Resgata a chave da API
api_key = os.environ.get("GEMINI_API_KEY")

# Área de Entrada de Dados do Pátio
prompt = st.text_area(
    "📝 Relato Técnico / Sintomas ou Solicitação de Esquema Elétrico:", 
    placeholder="Ex: Fox 1.6 MSI falha na borboleta. Preciso do esquema elétrico do corpo de borboleta e pinagem do módulo.\nEx 2: Nivus 1.0 TSI com erro de sensor de fase, mandando foto do osciloscópio...",
    height=120
)

# Campo para Envio de Arquivos (Fotos, Vídeos ou Áudios)
arquivo_enviado = st.file_uploader(
    "📸 Insira as mídias do pátio (Foto do Scanner, Gráfico do Osciloscópio, etc.):", 
    type=["png", "jpg", "jpeg", "mp4", "mov", "avi", "mp3", "wav", "m4a", "ogg"]
)

# Feedback visual das mídias carregadas
if arquivo_enviado is not None:
    if arquivo_enviado.type.startswith('image'):
        st.image(arquivo_enviado, caption="Análise Visual Ativada 🔍", use_container_width=True)
    elif arquivo_enviado.type.startswith('video'):
        st.video(arquivo_enviado)
        st.info("Análise de Vídeo Ativada 🎥")
    elif arquivo_enviado.type.startswith('audio'):
        st.audio(arquivo_enviado)
        st.info("Análise Acústica Ativada 🎵")

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
        parts.append({
            "inlineData": {
                "mimeType": midia.type,
                "data": base64_arquivo
            }
        })
        midia.seek(0)
        
    parts.append({"text": contexto_prompt})
    payload = {"contents": [{"parts": parts}]}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        dados_retorno = response.json()
        return dados_retorno['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Erro no servidor do Google (Código {response.status_code}): {response.text}"

# PROMPT DE ENGENHARIA SUPREMA COM FOCO EM ESQUEMAS ELÉTRICOS E OSCILOSCÓPIO
DIRETRIZ_SUPREMA_TECNICA = """
Você é o ápice da inteligência artificial automotiva, atuando como Engenheiro-Chefe de Fábrica e Mestre de Diagnóstico Avançado. Sua base de conhecimento inclui mapeamento completo de injeção eletrônica, redes de comunicação (CAN alta/baixa, LIN), diagramas elétricos, pinagens de módulos e parametrização detalhada de osciloscópios.

Sempre que sugerir ou analisar testes que envolvam OSCILOSCÓPIO ou TRANSDUTORES DE MOTOR, você DEVE fornecer as instruções de configuração de forma ultra-detalhada para o mecânico no pátio, incluindo:

1. GUIA DE CONEXÃO DO OSCILOSCÓPIO:
   - Indique exatamente onde conectar a ponta de prova/agulha do Canal (ex: Canal 1 no pino X do sensor, correspondente ao fio de sinal).
   - Indique onde conectar a garra de jacaré do aterramento (ex: carcaça do motor, aterramento de referência do sensor ou negativo da bateria) para evitar ruídos na imagem.

2. CONFIGURAÇÃO DE ESCALA DA TELA:
   - Forneça o ajuste de TENSÃO por divisão ideal (ex: 1V/div, 2V/div, 5V/div) para que o sinal preencha a tela perfeitamente sem cortar.
   - Forneça o ajuste de TEMPO por divisão ideal (ex: 2ms/div, 10ms/div, 500ms/div) para capturar ciclos completos do sinal ou o evento exato (como o tempo de centelha ou disparo do bico).
   - Se aplicável, mencione o tipo de Trigger recomendado (Borda de subida/descida, canal de referência) para congelar a onda na tela.

3. PADRÃO DE ONDA ESPERADO (REFERÊNCIA DE BOM FUNCIONAMENTO):
   - Descreva como deve ser o desenho correto na tela (ex: sinal de onda quadrada variando estritamente de 0V a 5V para sensores Hall, onda senoidal pura para indutivos, gráfico característico de disparo indutivo com pico de alta tensão para bobinas).

Formate sua resposta técnica rigorosamente com estes títulos explicativos:
### 📋 Dados Técnicos Extraídos & Parâmetros do Veículo
### ⚡ Análise Elétrica e Lógica de Falhas
### 🛠️ Mapeamento de Esquema Elétrico & Pinagens
### 🔬 Guia do Osciloscópio (Conexão, Tempo
