import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro - Diagnóstico")

# Campos de entrada
dtc = st.text_input("Código de Falha (DTC):")
veiculo = st.text_input("Modelo:")
tarefa = st.selectbox("Objetivo:", ["Diagnóstico", "Causas", "Esquema", "Osciloscópio"])
btn = st.button("Consultar Base Técnica")

if btn:
    if not dtc or not veiculo:
        st.warning("Preencha o DTC e o Veículo.")
    else:
        try:
            # Configuração da chave
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            
            # Usando a versão mais robusta disponível
            model = genai.GenerativeModel('gemini-pro')
            
            with st.spinner("Consultando..."):
                prompt = f"Analise o {veiculo} com erro {dtc}. Tarefa: {tarefa}. Seja técnico."
                response = model.generate_content(prompt)
                st.markdown("### Resultado:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Erro no sistema: {e}")
            st.info("Dica: Verifique se sua API Key no Google AI Studio está ativa e se você aceitou os termos de uso recentes.")
