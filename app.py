import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Oficina Pro", layout="wide")
st.title("⚙️ Oficina Pro")

# Configuração minimalista
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

dtc = st.text_input("DTC:")
veiculo = st.text_input("Veículo:")
btn = st.button("Consultar")

if btn:
    try:
        # Usando o modelo padrão antigo, que costuma ser mais permissivo em contas novas
        model = genai.GenerativeModel('gemini-pro')
        
        with st.spinner("Analisando..."):
            response = model.generate_content(f"Analise o {veiculo} com código {dtc}. Seja técnico e preciso.")
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Erro ao consultar: {e}")
