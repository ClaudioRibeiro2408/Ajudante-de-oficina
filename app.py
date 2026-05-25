import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Oficina Pro Multimodal", layout="wide")
st.title("⚙️ Oficina Pro - Diagnóstico com IA")

# O modelo 'gemini-1.5-flash' é o que aceita imagens e vídeos
model = genai.GenerativeModel('gemini-1.5-flash')

# Upload de arquivos (Fotos e vídeos)
arquivo = st.file_uploader("Envie foto ou vídeo do problema/osciloscópio", type=['jpg', 'png', 'mp4'])

veiculo = st.text_input("Veículo/Motor:")
descricao = st.text_area("Descreva o sintoma:")

if st.button("Gerar Diagnóstico Técnico"):
    if arquivo:
        # Aqui o código processaria o arquivo para a IA
        st.info("Processando arquivo e analisando esquemas técnicos...")
        # Lógica de integração multimodal aqui
    else:
        st.warning("Por favor, anexe uma imagem ou vídeo para um diagnóstico mais preciso.")
