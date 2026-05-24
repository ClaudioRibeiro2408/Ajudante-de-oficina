import streamlit as st
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Oficina Pro", layout="centered")
st.title("⚙️ Oficina Pro - Diagnóstico IA")

# COLOCAR A CHAVE AQUI OU NO SECRETS
api_key = st.text_input("Insira sua API Key do Google (Google AI Studio):", type="password")

veiculo = st.text_input("Modelo do carro:")
queixa = st.text_area("Descreva o problema:")

if st.button("Pesquisar Diagnóstico Técnico"):
    if api_key and veiculo and queixa:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Você é um mecânico especialista. Analise o veículo {veiculo} com o sintoma: {queixa}. Liste causas prováveis, testes técnicos para confirmar e o que verificar primeiro."
            
            with st.spinner("IA pesquisando nos bancos de dados automotivos..."):
                response = model.generate_content(prompt)
                st.success("Diagnóstico Gerado:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Erro ao conectar com a IA: {e}")
    else:
        st.warning("Preencha todos os campos e a API Key.")
