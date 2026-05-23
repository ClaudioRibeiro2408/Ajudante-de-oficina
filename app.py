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
st.subheader("Central Unificada de Diagnóstico, Laudos e Esquemas Elétricos")
st.write("---")

# Resgata a chave da API
api_key = os.environ.get("GEMINI_API_KEY")

# Área de Entrada de Dados do Pátio
prompt = st.text_area(
    "📝 Relato Técnico / Sintomas ou Solicitação de Esquema Elétrico:", 
    placeholder="Ex 1: Fox 1.6 MSI falha na borboleta. Preciso do esquema elétrico do corpo de borboleta e pinagem do módulo.\nEx 2: Nivus 1.0 TSI com erro de sensor de fase, mandando foto do osciloscópio...",
    height=120
)

# Upload de Arquivos Expandido
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

# PROMPT DE ENGENHARIA SUPREMA COM FOCO EM ESQUEMAS ELÉTRICOS
DIRETRIZ_SUPREMA_TECNICA = """
Você é o ápice da inteligência artificial automotiva, atuando como Engenheiro-Chefe de Fábrica e Mestre de Diagnóstico Avançado. Sua base de conhecimento inclui mapeamento completo de injeção eletrônica, redes de comunicação (CAN alta/baixa, LIN), diagramas elétricos e pinagens de módulos de controle (ECU/ECM).

Sempre que o mecânico solicitar um diagnóstico, um defeito ou pedir explicitamente ESQUEMAS ELÉTRICOS, PINAGENS ou INFORMAÇÕES TÉCNICAS de reparo, estruture sua resposta com precisão milimétrica seguindo as regras abaixo:

1. MAPEAMENTO ELÉTRICO E PINAGEM (SEMPRE QUE SOLICITADO OU RELEVANTE PARA O DEFEITO):
   - Descreva detalhadamente a pinagem do componente citado (ex: Sensor MAP, Corpo de Borboleta, Sonda Lambda, Pedor do Acelerador).
   - Indique a função de cada fio/pino: Alimentação (+5V, +12V), Aterramento de Sensores (Massa), Sinal de Retorno, Linha de Comunicação ou Sinal PWM.
   - Forneça os valores de referência para medição com multímetro (tensão esperada com chave ligada e motor funcionando) e com osciloscópio.

2. INFORMAÇÕES TÉCNICAS DE MECÂNICA E ENGENHARIA:
   - Forneça dados de torque de aperto fundamentais (se correlacionados ao componente, ex: cabeçote, velas, sensores).
   - Indique folgas nominais, diagramas de sincronismo virtual (Fase e Rotação) e procedimentos de ajuste/aprendizado via scanner pós-troca.
   - Detalhe especificações de fluidos e pressões nominais (ex: linha de combustível da família VW EA211 TSI/MSI e multimarcas).

3. DIAGNÓSTICO INTEGRADO (TEXTO E MÍDIA):
   - Cruze fotos de scanners (DTCs), oscilogramas ou ruídos de áudio/vídeo com os diagramas elétricos para determinar se a falha é no chicote (curto ao positivo, curto à massa, circuito aberto), no sensor ou na própria ECU.

Formate sua resposta técnica rigorosamente com estes títulos explicativos:
### 📋 Dados Técnicos Extraídos & Parâmetros do Veículo
### ⚡ Análise Elétrica e Lógica de Falhas
### 🛠️ Mapeamento de Esquema Elétrico & Pinagens (Alimentação, Sinal e Massa)
### 🔍 Roteiro Prático de Testes (Passo a passo no carro com Osciloscópio/Multímetro)
### 💡 Diagnóstico Provável & Causa Raiz
"""

DIRETRIZ_SUPREMA_CLIENTE = """
Você é o Diretor de Atendimento de uma oficina mecânica premium. Traduza o defeito ou necessidade de reparo técnico em um laudo comercial transparente, amigável e profissional para o WhatsApp do cliente.
Destaque que a oficina está usando diagramas elétricos de fábrica e equipamentos avançados para garantir que o carro seja consertado sem tentativas e erros. Use tópicos limpos e emojis. Não mencione códigos de pinos ou valores técnicos difíceis para o cliente. Termine dizendo que a equipe está finalizando a cotação.
"""

# Execução do Botão Técnico
if botao_tecnico and (prompt or arquivo_enviado):
    if not api_key:
        st.error("Chave da API não configurada nos Segredos do Streamlit.")
    else:
        with st.spinner("🚀 Consultando Engenharia de Fábrica e Esquemas Elétricos..."):
            contexto = f"{DIRETRIZ_SUPREMA_TECNICA}\n\nSolicitação do Mecânico:\nTexto: {prompt}\nMídia: Analisar anexo se houver."
            resposta = chamar_gemini(contexto, arquivo_enviado)
            st.success("Informações Técnicas e Esquema Elétrico Gerados!")
            st.markdown(resposta)

# Execução do Botão Cliente
if botao_cliente and (prompt or arquivo_enviado):
    if not api_key:
        st.error("Chave da API não configurada nos Segredos do Streamlit.")
    else:
        with st.spinner("✍️ Convertendo para linguagem comercial premium..."):
            contexto = f"{DIRETRIZ_SUPREMA_CLIENTE}\n\nDados da Oficina:\nTexto: {prompt}\nMídia: Analisar anexo se houver."
            resposta = chamar_gemini(contexto, arquivo_enviado)
            st.success("Laudo Comercial Premium Gerado!")
            st.info("💡 Pronto para cópia! Cole direto no WhatsApp do cliente:")
            st.markdown(resposta)
            st.balloons()

elif (botao_tecnico or botao_cliente):
    st.error("Atenção: Digite o veículo/sintoma ou peça o esquema elétrico no campo de texto antes de clicar.")
