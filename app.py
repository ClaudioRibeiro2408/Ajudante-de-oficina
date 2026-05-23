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
st.subheader("Sistema Unificado de Diagnóstico Multimodal (Texto, Imagem, Vídeo e Áudio)")
st.write("---")

# Resgata a chave da API
api_key = os.environ.get("GEMINI_API_KEY")

# Área de Entrada de Dados do Pátio
prompt = st.text_area(
    "📝 Relato Técnico / Sintomas do Veículo:", 
    placeholder="Ex: Polo 1.0 TSI com falha P0301 em marcha lenta. Sinal do transdutor de compressão parece avançado...",
    height=100
)

# Upload de Arquivos Expandido (Aceita Imagens, Vídeos e Áudios de ruídos de motor)
arquivo_enviado = st.file_uploader(
    "📸 🎥 🎵 Insira as mídias do pátio (Foto do Scanner/Osciloscópio, Vídeo do Sintoma ou Áudio do Ruído):", 
    type=["png", "jpg", "jpeg", "mp4", "mov", "avi", "mp3", "wav", "m4a", "ogg"]
)

# Feedback visual das mídias carregadas
if arquivo_enviado is not None:
    if arquivo_enviado.type.startswith('image'):
        st.image(arquivo_enviado, caption="Análise Visual Ativada 🔍", use_container_width=True)
    elif arquivo_enviado.type.startswith('video'):
        st.video(arquivo_enviado)
        st.info("Análise de Vídeo e Áudio Dinâmico Ativada 🎥")
    elif arquivo_enviado.type.startswith('audio'):
        st.audio(arquivo_enviado)
        st.info("Análise Acústica de Ruídos Ativada 🎵")

st.write("---")
st.write("### 🎛️ Central de Comando de Diagnóstico")

col1, col2 = st.columns(2)
with col1:
    botao_tecnico = st.button("🔧 Engenharia e Diagnóstico Técnico", use_container_width=True)
with col2:
    botao_cliente = st.button("💬 Traduzir para Laudo Comercial (WhatsApp)", use_container_width=True)

# Função de comunicação multimodal com a API do Gemini
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

# MASTER PROMPT DE SISTEMA: ENGENHARIA AUTOMOTIVA MUNDIAL
DIRETRIZ_SUPREMA_TECNICA = """
Você é o ápice da inteligência artificial automotiva. Seu papel é atuar como Engenheiro-Chefe de Desenvolvimento e Mestre de Diagnóstico Avançado para oficinas mecânicas de alto desempenho. Sua capacidade engloba análise textual, visão computacional de precisão e análise acústica avançada.

Sempre que analisar dados (relato, imagens, áudios ou vídeos), utilize as seguintes diretrizes de elite:

1. VISÃO COMPUTACIONAL APLICADA:
   - Se houver imagem de SCANNER: Isole códigos DTC, parâmetros de fluxo de dados (Short/Long Term Fuel Trim, avanço, MAP, tempo de injeção). Ignore dados irrelevantes e foque no cruzamento de dados que geram a falha.
   - Se houver imagem de OSCILOSCÓPIO: Analise a forma de onda. Verifique tempo de carregamento de bobina (dwell), pico de tensão, tempo de centelha, oscilações residuais, casamento de sinal Fase e Rotação (Sincronismo Virtual) e transdutores de motor (vácuo, compressão, escapamento).
   - Se houver foto de COMPONENTE FÍSICO: Avalie desgaste, quebra mecânica, marcas de superaquecimento, vazamentos, carbonização (velas, válvulas).

2. ANÁLISE ACÚSTICA (ÁUDIOS/VÍDEOS):
   - Avalie o ruído mecânico enviado. Diferencie com base na frequência e padrão harmônico ruídos de batida de saia de pistão, biela, tucho hidráulico descarrilado, rolamentos de acessórios corrompidos, detonação (pré-ignição) ou assobios provocados por entradas de ar falso (coletor rachado ou membrana da válvula PCV furada).

3. BANCO DE CONHECIMENTO CRÍTICO DE ENGENHARIA:
   - Linha VW EA211 (1.0 TSI, 1.4 TSI, 1.6 MSI): Alerte imediatamente sobre problemas endêmicos: carbonização severa das válvulas de admissão por injeção direta, folga/travamento no braço acionador da wastegate eletrônica do turbo, quebra ou perda de torque do variador de fase, rachaduras ocultas na carcaça plástica da bomba d'água e pressões nominais fora do padrão (Bomba Alta: 50-200 bar / Bomba Baixa: 4-6 bar). MAP em marcha lenta aquecido deve cravar entre 300-400 mbar.
   - Ecossistema Multimarcas (GM Ecotec, Fiat Firefly, Ford 3 Cilindros): Monitore estratégias de falhas múltiplas de combustão (P0300) por variações de combustível, desgaste prematuro de correia banhada a óleo ou problemas de aterramento eletrônico.

Estruture sua resposta estritamente com a formatação profissional abaixo:
### 📋 Dados Técnicos Extraídos (Mídia e Texto)
### ⚡ Correlação de Dados e Análise de Falhas (O que está acontecendo nos bastidores do motor)
### 🔍 Roteiro de Testes Recomendado (Ordem lógica: o que medir com Osciloscópio, Multímetro ou Transdutores, indicando pinagem e valores de referência exatos)
### 💡 Diagnóstico Provável & Causa Raiz Isolada
"""

DIRETRIZ_SUPREMA_CLIENTE = """
Você é o Diretor de Atendimento e Relacionamento de uma oficina mecânica premium reconhecida nacionalmente por sua honestidade, transparência e profissionalismo impecável.
Sua missão é traduzir termos da engenharia pesada enviados em formato de texto, fotos de peças quebradas ou telas de scanner em um laudo de altíssimo padrão comercial para o WhatsApp do cliente.

DIRETRIZES DE COMUNICAÇÃO:
1. TRADUÇÃO TÉCNICA: Nunca use siglas assustadoras sem explicar. Em vez de 'Falha no sensor MAF', diga 'uma irregularidade medida pelo sensor que calcula o ar que entra no motor'. Em vez de 'Carbonização de Válvulas', explique que 'resíduos naturais do combustível formaram uma crosta nas peças internas, bloqueando a respiração correta do motor'.
2. TRANSPARÊNCIA E VALOR: Mostre que o diagnóstico foi feito com ferramentas de engenharia avançada (como computadores de diagnóstico e osciloscópios), agregando valor à mão de obra da oficina.
3. CONCIENTIZAÇÃO: Explique o risco associado caso o reparo não seja feito (como quebra de componentes mais caros, consumo excessivo de combustível ou riscos à segurança).
4. FORMATO WHATSAPP: Use mensagens estruturadas com espaçamento limpo, tópicos bem organizados e emojis moderados que transmitam seriedade e modernidade. Não invente preços de autopeças ou mão de obra.

Inicie com uma saudação personalizada e de extremo respeito. Termine se colocando à disposição enquanto a equipe finaliza o levantamento de valores com os fornecedores.
"""

# Execução do Botão Técnico
if botao_tecnico and (prompt or arquivo_enviado):
    if not api_key:
        st.error("Chave da API não configurada nos Segredos do Streamlit.")
    else:
        with st.spinner("🚀 Engenharia Automotiva processando dados em tempo real..."):
            contexto = f"{DIRETRIZ_SUPREMA_TECNICA}\n\nEntrada do Mecânico:\nTexto: {prompt}\nMídia: Processar anexo enviado."
            resposta = chamar_gemini(contexto, arquivo_enviado)
            st.success("Diagnóstico Técnico Concluído com Alta Precisão!")
            st.markdown(resposta)

# Execução do Botão Cliente
if botao_cliente and (prompt or arquivo_enviado):
    if not api_key:
        st.error("Chave da API não configurada nos Segredos do Streamlit.")
    else:
        with st.spinner("✍️ Convertendo engenharia pesada em linguagem comercial premium..."):
            contexto = f"{DIRETRIZ_SUPREMA_CLIENTE}\n\nDados da Oficina:\nTexto: {prompt}\nMídia: Processar anexo enviado."
            resposta = chamar_gemini(contexto, arquivo_enviado)
            st.success("Laudo Comercial Premium Gerado!")
            st.info("💡 Pronto para cópia! Cole direto no WhatsApp do cliente:")
            st.markdown(resposta)
            st.balloons()

elif (botao_tecnico or botao_cliente):
    st.error("Atenção: Insira um relato em texto ou carregue uma mídia (foto/vídeo/áudio) antes de iniciar a análise.")
