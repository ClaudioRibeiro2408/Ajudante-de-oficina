import streamlit as st
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Oficina Pro - Diagnóstico Técnico", layout="wide")

# Inicialização da API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Erro ao carregar a chave do Secrets. Verifique se o nome no painel Secrets é exatamente 'GOOGLE_API_KEY'.")
    st.stop()

st.title("⚙️ Oficina Pro - Diagnóstico Técnico")

# Interface
col1, col2 = st.columns([1, 2])

with col1:
    dtc = st.text_input("Código de Falha (DTC) Ex: P0300:")
    veiculo = st.text_input("Modelo e Motorização:")
    tarefa = st.selectbox("O que você precisa?", 
                          ["Diagnóstico Completo", 
                           "Causas Prováveis", 
                           "Esquema Elétrico (Descrição)", 
                           "Dicas de Osciloscópio (Sinais e Conexão)"])
    
    btn_analisar = st.button("Consultar Base Técnica")

with col2:
    if btn_analisar:
        if dtc and veiculo:
            prompt = f"Como mecânico especialista, analise o {veiculo} com código {dtc}. Objetivo: {tarefa}. Seja técnico e preciso."
            with st.spinner("Consultando manuais..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown("### Resultado:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro ao consultar: {e}")
        else:
            st.warning("Preencha o DTC e o modelo.")
