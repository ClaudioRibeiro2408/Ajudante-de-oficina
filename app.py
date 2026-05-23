import streamlit as st
import requests
import json
import os
import mimetypes

# Configuração da página
st.set_page_config(page_title="Oficina Inteligente", layout="centered")

st.title("🚀 Oficina Inteligente")
st.subheader("Sistema de Diagnóstico Visual e por Texto")
st.write("---")

# Resgata a chave da API
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        from google.colab import userdata
        api_key = userdata.get('GEMINI_API_KEY')
    except:
        pass

# Campo de texto estilo WhatsApp
prompt = st.text_area(
    "O que aconteceu com o veículo?", 
    placeholder="Ex: Gol 1.0 TSI falhando. Veja a foto do scanner ou o vídeo do motor...",
    height=100
)

# NOVO: Campo para enviar Fotos ou Vídeos direto do celular/computador
arquivo_enviado = st.file_uploader(
    "📸 Envie uma foto do scanner, peça com defeito ou um vídeo curto do sintoma:", 
    type=["png", "jpg", "jpeg", "mp4", "mov", "avi"]
)

# Mostra uma prévia do arquivo na tela se for imagem
if arquivo_enviado is not None:
    if arquivo_enviado.type.startswith('image'):
        st.image(arquivo_enviado, caption="Arquivo carregado com sucesso!", use_container_width=True)
    elif arquivo_enviado.type.startswith('video'):
        st.video(arquivo_enviado)

botao = st.button("🔧 Processar Diagnóstico Avançado", use_container_width=True)

if botao and (prompt or arquivo_enviado):
    if not api_key:
        st.error("Chave da API não encontrada no ambiente do Colab.")
    else:
        with st.spinner("🤖 O Mecânico Master está analisando o texto e a mídia... Aguarde..."):
            try:
                # URL para o modelo robusto atualizado
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
                
                contexto = f"""
                Você é um Engenheiro Automotivo Especialista e Consultor Técnico de Oficina Mecânica de Alta Performance.
                Analise o relato do mecânico e QUALQUER imagem ou vídeo enviado (como telas de scanner, osciloscópio, peças ou comportamento do motor).
                Devolva uma resposta formatada exatamente com os seguintes tópicos em Markdown:
                
                ### 📋 Dados Identificados
                * **Veículo/Motor:** (Identifique o veículo, motorização ou marcas se visíveis ou citadas)
                * **Evidência Visual:** (Descreva o que você identificou na foto ou vídeo enviado, ex: códigos na tela do scanner, peça danificada, etc. Se não houver mídia, diga 'Apenas texto fornecido')
                
                ### ⚡ Análise Técnica de Falhas
                * (Liste os códigos de erro DTC ou anomalias físicas encontradas e explique o significado técnico detalhado de cada um)
                
                ### 🔍 Próximos Testes Recomendados (O que testar no pátio?)
                * (Cite de 3 a 4 testes mecânicos ou eletrônicos práticos com valores de referência usando multímetro, osciloscópio ou manômetro para isolar a causa raiz. Seja direto, de mecânico para mecânico)
                
                ### 💡 Diagnóstico Provável & Causa Raiz
                * (Qual o componente ou sistema tem a maior probabilidade de estar causando o problema técnico relatado/visto?)
                
                Relato do mecânico: {prompt if prompt else 'O mecânico enviou apenas a mídia para análise.'}
                """
                
                # Monta a estrutura de peças do pacote (Parts)
                parts = []
                
                # Se tiver arquivo (Foto/Vídeo), converte para enviar na API
                if arquivo_enviado is not None:
                    bytes_arquivo = arquivo_enviado.read()
                    import base64
                    base64_arquivo = base64.b64encode(bytes_arquivo).decode('utf-8')
                    
                    parts.append({
                        "inlineData": {
                            "mimeType": arquivo_enviado.type,
                            "data": base64_arquivo
                        }
                    })
                
                # Adiciona o texto de instruções e o prompt
                parts.append({"text": contexto})
                
                payload = {
                    "contents": [{
                        "parts": parts
                    }]
                }
                headers = {'Content-Type': 'application/json'}
                
                # Envia o sinal completo (Mídia + Texto) pro Google
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 200:
                    dados_retorno = response.json()
                    texto_ia = dados_retorno['candidates'][0]['content']['parts'][0]['text']
                    st.success("Análise Multimodal Concluída!")
                    st.markdown(texto_ia)
                    st.balloons()
                else:
                    st.error(f"Erro no servidor do Google (Código {response.status_code}): {response.text}")
                
            except Exception as e:
                st.error(f"Erro de conexão no pátio digital: {e}")
            
elif botao:
    st.error("Por favor, digite um relato ou envie uma foto/vídeo antes de clicar em processar.")
