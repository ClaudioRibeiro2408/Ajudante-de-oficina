import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="centered")
st.title("⚙️ Oficina Pro - Diagnóstico")

# A configuração da API é feita dentro de uma função, não no carregamento da página
def consultar_ia(veiculo, dtc, descricao):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Veículo: {veiculo}. DTC: {dtc}. Problema: {descricao}. Me dê o diagnóstico."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro técnico na conexão: {str(e)}"

# Interface que sempre carrega
veiculo = st.text_input("Veículo:")
dtc = st.text_input("DTC:")
descricao = st.text_area("Descrição:")

if st.button("Consultar"):
    with st.spinner("Conectando..."):
        resultado = consultar_ia(veiculo, dtc, descricao)
        st.write(resultado)
