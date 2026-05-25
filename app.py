import streamlit as st
import google.generativeai as genai

st.title("Oficina Pro - Diagnóstico")

# Configuração minimalista
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

veiculo = st.text_input("Veículo:", value="Onix 1.4 2018")
dtc = st.text_input("DTC:", value="P0420")
descricao = st.text_area("Descrição:", value="Luz da injeção acesa")

if st.button("Consultar"):
    try:
        with st.spinner("Analisando..."):
            prompt = f"Diagnostique o falha {dtc} no {veiculo}. Descrição: {descricao}. Seja técnico e direto."
            # Chamada simples e direta
            response = model.generate_content(prompt)
            st.write(response.text)
    except Exception as e:
        st.error(f"Erro: {e}")
