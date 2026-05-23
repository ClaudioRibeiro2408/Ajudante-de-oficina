import streamlit as st
import requests
import json
import os
import base64

# Configuração da página
st.set_page_config(page_title="Oficina Inteligente", layout="centered")

st.title("🚀 Oficina Inteligente")
st.subheader("Sistema de Diagnóstico Técnico e Laudos para Clientes")
st.write("---")

# Resgata a chave da API das variáveis de ambiente ou segredos do Streamlit
api_key = os.environ.get("GEMINI_API_KEY")

# Campo de texto estilo WhatsApp
prompt = st.text_area(
    "O que aconteceu com o veículo?", 
    placeholder="Ex: Onix 1.4 2018 acendendo luz de injeção, código P0420 no scanner...",
    height=100
)

# Campo para enviar Fotos ou Vídeos
arquivo_enviado = st.file_uploader(
    "📸 Envie uma foto do scanner, peça com defeito ou um vídeo curto do sintoma:", 
    type=["png", "jpg", "jpeg", "mp4", "mov", "avi"]
)

# Mostra uma prévia do arquivo na tela se for imagem ou vídeo
if arquivo_enviado is not None:
    if arquivo_enviado.type.startswith('image'):
        st.image(arquivo_enviado, caption="Arquivo carregado com sucesso!", use_container_width=True)
    elif arquivo_enviado.type.startswith('video'):
        st.video(arquivo_enviado)

st.write("### 🎛️ O que você deseja gerar?")

# Cria duas colunas para os botões ficarem lado a lado
col1, col2 = st.columns(2)

with col1:
    botao_tecnico = st.button("🔧 Diagnóstico Técnico", use_container_width=True)

with col2:
    botao_cliente = st.button("💬 Laudo para o Cliente", use_container_width=True)

# Função para disparar a API do Gemini
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
        # Reseta o ponteiro do arquivo para caso precise ler de novo
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

# Ação se clicar no botão TÉCNICO
if botao_tecnico and (prompt or arquivo_enviado):
    if not api_key:
        st.error("Chave da API não encontrada nos Segredos do Streamlit.")
    else:
        with st.spinner("🤖 O Mecânico Master está analisando os dados técnicos..."):
            contexto = f"""
            Você é um Engenheiro Automotivo Especialista e Consultor Técnico de Oficina Mecânica de Alta Performance.
            Analise o relato e qualquer imagem fornecida e devolva uma resposta técnica estruturada exatamente com os títulos:
            ### 📋 Dados Identificados
            ### ⚡ Análise Técnica de Falhas
            ### 🔍 Próximos Testes Recomendados (O que testar no pátio?)
            ### 💡 Diagnóstico Provável & Causa Raiz
            
            Seja direto, use termos técnicos exatos (osciloscópio, multímetro, pressões). De mecânico para mecânico.
            Relato: {prompt if prompt else 'Mídia enviada para análise.'}
            """
            resposta = chamar_gemini(contexto, arquivo_enviado)
            st.success("Análise Técnica Concluída!")
            st.markdown(resposta)

# Ação se clicar no botão CLIENTE (WhatsApp)
if botao_cliente and (prompt or arquivo_enviado):
    if not api_key:
        st.error("Chave da API não encontrada nos Segredos do Streamlit.")
    else:
        with st.spinner("✍️ Traduzindo o diagnóstico para uma linguagem simples e profissional..."):
            contexto = f"""
            Você é um Consultor de Atendimento de uma oficina mecânica premium, conhecido pela transparência e excelente comunicação.
            Sua missão é pegar o relato do problema e as imagens fornecidas (como fotos de peças ruins ou códigos de erro) e gerar um texto amigável, claro, didático e altamente profissional para ser enviado diretamente no WhatsApp do cliente.
            
            DIRETRIZES DO TEXTO:
            1. Use uma linguagem simples. Em vez de termos como 'DTC P0420', diga 'uma falha registrada no sistema de controle de emissões'. Em vez de 'sonda lambda travada', explique que 'o sensor que mede os gases não está trabalhando como deveria'.
            2. Seja cordial e use tópicos limpos com emojis adequados para facilitar a leitura no celular.
            3. Explique brevemente o risco de não consertar (ex: aumento de consumo de combustível, perda de potência ou danos a outras peças mais caras).
            4. NÃO invente valores de orçamento ou preços de peças. Termine o texto com uma frase deixando claro que a equipe técnica está finalizando o levantamento de peças para passar os valores exatos.
            
            Estruture a resposta com um visual limpo e uma saudação inicial amigável (ex: 'Olá! Tudo bem? Aqui é da equipe técnica da oficina...').
            Relato do problema: {prompt if prompt else 'O mecânico enviou uma foto do defeito para avaliação.'}
            """
            resposta = chamar_gemini(contexto, arquivo_enviado)
            st.success("Laudo para WhatsApp Gerado com Sucesso!")
            st.info("💡 Dica: Você pode copiar o texto abaixo e colar direto no WhatsApp do seu cliente.")
            st.markdown(resposta)
            st.balloons()
            
elif (botao_tecnico or botao_cliente):
    st.error("Por favor, digite um relato ou envie uma foto/vídeo antes de processar.")
