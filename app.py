import streamlit as st
import google.generativeai as genai

# Configuração simples
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# FORÇANDO o modelo sem carregar listas ou versões beta
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("⚙️ Oficina Pro")
dtc = st.text_input("DTC:")
veiculo = st.text_input("Veículo:")

if st.button("Consultar"):
    try:
        response = model.generate_content(f"Analise o {veiculo} com código {dtc}.")
        st.write(response.text)
    except Exception as e:
        st.error(f"Erro detectado: {e}")
