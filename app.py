import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro - Diagnóstico Avançado", layout="wide")

st.title("⚙️ Oficina Pro - Diagnóstico Técnico")

# Configuração da API
api_key = st.sidebar.text_input("Insira sua API Key (Google AI Studio):", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    col1, col2 = st.columns(2)

    with col1:
        dtc = st.text_input("Código de Falha (DTC) Ex: P0300:")
        veiculo = st.text_input("Modelo e Motorização:")
        tarefa = st.selectbox("O que você precisa?", ["Causas Prováveis", "Esquema Elétrico (Descrição)", "Dicas de Osciloscópio"])

    with col2:
        if st.button("Consultar Base Técnica"):
            if dtc and veiculo:
                prompt = f"""
                Você é um engenheiro automotivo especialista. 
                Veículo: {veiculo}. 
                Código DTC: {dtc}.
                Tarefa: {tarefa}.
                Forneça uma explicação técnica precisa, direta e profissional.
                Se for esquema elétrico ou osciloscópio, descreva os pinos e os ajustes de tensão/tempo.
                """
                
                with st.spinner("Consultando manuais técnicos..."):
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("### Resultado da Pesquisa:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Erro na consulta: {e}")
            else:
                st.warning("Preencha o DTC e o modelo do veículo.")
else:
    st.info("Por favor, insira sua chave de API no menu lateral para começar.")
